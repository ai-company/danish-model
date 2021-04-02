# danish-model

[![Code style: black](https://img.shields.io/badge/Code%20Style-Black-black)]

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

### Notes for Mr Bug
#### Things that can be relevant.

1. The sentences are stripped.