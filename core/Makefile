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
