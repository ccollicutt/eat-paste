# Makefile for eat-paste

# Variables
IMAGE_NAME = eat-paste
CONTAINER_NAME = eat-paste
HOST_PORT = 5000
CONTAINER_PORT = 8000

# Targets
.PHONY: all build run stop curl logs

all: build run

build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run -d --name $(CONTAINER_NAME) -p $(HOST_PORT):$(CONTAINER_PORT) $(IMAGE_NAME) 

stop:
	docker container rm -f $(CONTAINER_NAME)

curl:
	echo "hi there" | \
	  curl -H "Content-Type: text/plain" \
	  -X POST \
	  --data-binary @- http://localhost:5000/paste

logs:
	docker logs $(CONTAINER_NAME)

test:
	python test_app.py