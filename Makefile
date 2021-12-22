ALL: build
	while true; do python server.py 2>&1; done

build:
	pip install -r requirements.txt
