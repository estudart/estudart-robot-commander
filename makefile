.PHONY: run up down build logs restart clean

run: up

build:
	docker compose build

up:
	docker compose up --build

logs:
	docker compose logs -f

down:
	docker compose down

restart: down up

clean:
	docker compose down --remove-orphans --volumes