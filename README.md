# danish-model

![Code style: black](https://img.shields.io/badge/Code%20Style-Black-black)

## Use a Python 3.8 environment.

A bundled danish language correction engine.


### Set-up

```sh
$ virtualenv -p /usr/bin/python3.8 .env
$ source .env/bin/activate
$ pip install -r requirements.txt
$ python -m spacy download da_core_news_lg
$ python tests.py
```

### Structure

#### `comma`

The commarization and punctuation model.

#### `data`

Tools for creating and manipulating datasets.

#### `preprocess`

Data preprocessing pipeline for getting data ready for training of comma model.

#### `spell`

The spelling algorithms and BERT interop layer.

#### `test_data`

Data for testing the whole pipeline.

### Notes for Mr Bug
#### Things that can be relevant.

1. The sentences are stripped.
