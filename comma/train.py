from __future__ import division

from time import time

import model, data
import pickle5 as pickle
import sys
import os.path
import data
import matplotlib.pyplot as plt

from os import path

import tensorflow as tf
import numpy as np
import tqdm

MAX_EPOCHS         = 50
MINIBATCH_SIZE     = 32
CLIPPING_THRESHOLD = 2.0
PATIENCE_EPOCHS    = 1

DATA_LEN = 0

def get_minibatch(file_name, batch_size, shuffle, with_pauses=False):

    with open(file_name, 'rb') as f:
        dataset = pickle.load(f)

    if shuffle:
        np.random.shuffle(dataset)

    X_batch = []
    Y_batch = []

    if len(dataset) < batch_size:
        lenwarning = (
        f"WARNING: Not enough samples in {file_name}. "
        f"Reduce mini-batch size to {len(dataset)} "
        f"or use a dataset with at least {MINIBATCH_SIZE * data.MAX_SEQUENCE_LEN} words."
        )
        print(lenwarning)

    print(f'Length of full dataset: {len(dataset)}')

    for subsequence in dataset:

        X_batch.append(subsequence[0])
        Y_batch.append(subsequence[1])

        if len(X_batch) == batch_size:

            X = np.array(X_batch, dtype=np.int32).T
            Y = np.array(Y_batch, dtype=np.int32).T

            yield X, Y

            X_batch = []
            Y_batch = []

@tf.function
def train_step(the_model, x, y):
    with tf.GradientTape() as tape:
        y_pred = the_model(x, training=True)
        loss   = model.cost(y_pred, y)

    gradients    = tape.gradient(loss, the_model.params)
    gradients, _ = tf.clip_by_global_norm(gradients, clip_norm=CLIPPING_THRESHOLD)

    optimizer.apply_gradients(zip(gradients, the_model.params))

    return loss

if __name__ == '__main__':
    starting_time = time()

    num_hidden      = int(sys.argv[2])
    learning_rate   = float(sys.argv[3])
    model_file_name = f'model_{sys.argv[1]}_{num_hidden}_{learning_rate}.pcl'

    print(num_hidden, learning_rate, model_file_name)

    rng = np.random
    rng.seed(1)

    print('Building model ...')

    vocab_len = len(data.read_vocabulary(data.WORD_VOCAB_FILE))
    x_len     = vocab_len if vocab_len < data.MAX_WORD_VOCABULARY_SIZE else data.MAX_WORD_VOCABULARY_SIZE + data.MIN_WORD_COUNT_IN_VOCAB
    x         = np.ones((x_len, MINIBATCH_SIZE)).astype(int)

    net       = model.GRU(rng, x, num_hidden)

    optimizer = tf.keras.optimizers.Adagrad(learning_rate=learning_rate, initial_accumulator_value=1e-6)

    starting_epoch = 0
    best_ppl       = np.inf

    validation_ppl_history = []

    print(f'Looking for model in: {os.path.join(data.DATA_PATH, model_file_name)}')

    if path.exists(os.path.join(data.DATA_PATH, model_file_name)):
        print(f'Found model: {model_file_name}')
        print('Loading the model and resuming training ...\n')

        net, stuff = model.load(os.path.join(data.DATA_PATH, model_file_name), x)

        learning_rate          = stuff[0]
        validation_ppl_history = stuff[1]
        starting_epoch         = stuff[2]
        rng                    = stuff[3]

    print('Training ...')

    for epoch in tqdm.tqdm(range(starting_epoch, MAX_EPOCHS), desc='Epochs'):
        t0 = time()

        total_neg_log_likelihood = 0
        total_num_output_samples = 0
        iteration = 0 

        print()
        for X, Y in tqdm.tqdm(get_minibatch(data.TRAIN_FILE, MINIBATCH_SIZE, shuffle=True), desc='Training'):
            loss = train_step(net, X, Y)

            total_neg_log_likelihood += loss
            total_num_output_samples += np.prod(Y.shape)
            iteration                += 1

            if iteration % 100 == 0:
                ppl   = np.exp(total_neg_log_likelihood / total_num_output_samples)
                validation_ppl_history.append(ppl)

                plt.plot(validation_ppl_history)
                plt.ylabel('Perplexity')
                plt.xlabel('Time')
                plt.title('Danish model - training')
                plt.savefig('perplexity.png')

                speed = total_num_output_samples / max(time() - t0, 1e-100)

                print(f'At iteration {iteration}, processed sentences in epoch: {iteration * MINIBATCH_SIZE}')
                sys.stdout.write(f'PPL: {ppl}; Speed:{speed} sps\n')
                sys.stdout.flush()

            if iteration % 500 == 0:
                print(f'Saving for good measure')
                model.save(net, model_file_name, learning_rate=learning_rate, validation_ppl_history=validation_ppl_history, best_validation_ppl=best_ppl, epoch=epoch, random_state=rng.get_state())

        print()
        print(f'Total number of training labels: {total_num_output_samples}')

        total_neg_log_likelihood = 0
        total_num_output_samples = 0

        for X, Y in tqdm.tqdm(get_minibatch(data.DEV_FILE, MINIBATCH_SIZE, shuffle=False), desc='Test'):
            total_neg_log_likelihood += model.cost(net(X, training=True), Y)
            total_num_output_samples += np.prod(Y.shape)

        print(f"Total number of validation labels: {total_num_output_samples}")

        ppl = np.exp(total_neg_log_likelihood / total_num_output_samples)

        print(f'Validation perplexity: {np.round(ppl, 4)}')

        if ppl <= best_ppl:
            best_ppl = ppl
            model.save(net, model_file_name, learning_rate=learning_rate, validation_ppl_history=validation_ppl_history, best_validation_ppl=best_ppl, epoch=epoch, random_state=rng.get_state())

    print('Finished !!!')
    print(f'Best validation perplexity: {best_ppl}')
    print(f'Total time: {time() - starting_time}')