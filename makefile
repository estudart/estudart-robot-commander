# Define variables for reuse
IMAGE_NAME = raspberry-pi-wss-server
CONTAINER_NAME = raspberry-pi-wss-server-container

# .PHONY tells Make these aren't files to be created
.PHONY: build up down clean

# Build the Docker image
build:
	docker build -t $(IMAGE_NAME) .

# Start the container
up:
	docker run -d --name $(CONTAINER_NAME) -p 8080:80 $(IMAGE_NAME)

# Run the service
run:
	docker build -t $(IMAGE_NAME) .
	docker run --name $(CONTAINER_NAME) -p 8080:80 $(IMAGE_NAME)

# Stop and remove the container
down:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

# Clean up local images
clean: down
	docker rmi $(IMAGE_NAME)
