build-dev:
	@if [ -z "$(version)" ]; then \
		docker build -t senchi-api-v1 .; \
	else \
		docker build -t senchi-api-v$(version) .; \
	fi

run-dev:
	@if [ -z "$(version)" ]; then \
		docker run --env-file .env -p 8000:8000 senchi-api-v1; \
	else \
		docker run --env-file .env -p 8000:8000 senchi-api-v$(version); \
	fi

up:
	# Remove the container if it exists
	@docker rm -f senchi-api-v1 || true
	@docker compose -f docker-compose.yml up -d --build

down:
	@docker compose -f docker-compose.yml down

restart:
	@docker compose -f docker-compose.yml down
	@docker compose -f docker-compose.yml up -d --build

build-and-run-dev:
	@echo "Building the docker image..."
	@make build-dev
	@echo "Running the docker container..."
	@make run-dev

