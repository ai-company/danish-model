ALL: build
	while true; do python server.py; done

build:
	pip install -r requirements.txt
	python -m spacy download da_core_news_lg
