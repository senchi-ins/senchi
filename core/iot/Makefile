PORT ?= 5000

start-ngrok:
	if [ -z $$(pgrep -f 'ngrok http $(PORT)') ]; then \
		ngrok http $(PORT); \
	fi

start-server:
	uvicorn core.iot.simple_webhook:app --reload --port $(PORT)

update-webhook:
	python switchbot.py

start-monitoring:
	@make start-ngrok & \
	@make start-server
	@make update-webhook