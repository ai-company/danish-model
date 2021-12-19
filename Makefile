ALL: build
	while true; do python server.py; done

build:
	pip install -r requirements.txt
