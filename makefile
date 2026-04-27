# =========================
# Variables
# =========================
API_IMAGE_NAME = raspberry-pi-wss-server
API_CONTAINER_NAME = raspberry-pi-wss-server-container

WORKER_IMAGE_NAME = raspberry-pi-worker
WORKER_CONTAINER_NAME = raspberry-pi-worker-container

.PHONY: build-api build-worker up-api up-worker down-api down-worker clean run

# =========================
# Build
# =========================
build-api:
	docker build -f Dockerfile.api -t $(API_IMAGE_NAME) .

build-worker:
	docker build -f Dockerfile.worker -t $(WORKER_IMAGE_NAME) .

build: build-api build-worker

# =========================
# Run containers
# =========================
up-api:
	docker run -d \
		--name $(API_CONTAINER_NAME) \
		-p 8000:8000 \
		$(API_IMAGE_NAME)

up-worker:
	docker run -d \
		--name $(WORKER_CONTAINER_NAME) \
		$(WORKER_IMAGE_NAME)

logs-api:
	docker logs -f $(API_CONTAINER_NAME)

logs-worker:
	docker logs -f $(WORKER_CONTAINER_NAME)

logs:
	@echo "Following logs for: $(API_CONTAINER_NAME) and $(WORKER_CONTAINER_NAME)"
	@docker logs -f $(API_CONTAINER_NAME) & docker logs -f $(WORKER_CONTAINER_NAME)

up: up-api up-worker logs

# =========================
# Stop & remove
# =========================
down-api:
	docker stop $(API_CONTAINER_NAME) || true
	docker rm $(API_CONTAINER_NAME) || true

down-worker:
	docker stop $(WORKER_CONTAINER_NAME) || true
	docker rm $(WORKER_CONTAINER_NAME) || true

down: down-api down-worker

# =========================
# Full run (build + up)
# =========================
run: build up

# =========================
# Cleanup
# =========================
clean: down
	docker rmi $(API_IMAGE_NAME) || true
	docker rmi $(WORKER_IMAGE_NAME) || true