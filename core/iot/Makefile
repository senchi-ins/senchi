PORT ?= 5000

start-ngrok:
	if [ -z $$(pgrep -f 'ngrok http $(PORT)') ]; then \
		ngrok http $(PORT); \
	fi

start-server:
	uvicorn wifi.simple_webhook:app --reload --port $(PORT)

update-webhook:
	uv run switchbot.py

start-monitoring:
	@echo "Updating webhook to begin monitoring..."
	@make update-webhook