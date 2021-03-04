# danish-model
A bundled danish language correction engine.

## Running

Simply install from `requirements.txt`, then run the following to install relevant spaCy model:

```
python -m spacy download da_core_news_lg
```

To try the model, run `comma/comma.py`.

## Approach

An innovative POS-tag centered way of restoring commas using a bidirectional GRU network.

## Structure

- `comma.py`

This script contains the bundled commarization function, and will run a commarization loop if run as `__main__`.

- `convert.py`

Contains universal helper functions for converting sentences into grammar tokens.
Currently some word types will be masked with POS tokens, while relevant others remain in their native form.

This is done to stimulate the danish grammar rules.

- `data.py`

Preprocessing script for handling input files. This covers splitting `train`, `dev` and `test` sets and gathering a vocabulary for use in the model.

- `explain.py`

This script is a working prototype of an explanation engine. Can explain danish commas in a sentence.

- `model.py`

Keras/TF code for a specialized bidirectional GRU network for punctuation.

- `train.py`

A script for training the model. Will initiate the training process when run as `__main__`.