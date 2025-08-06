# Ensure the mosquitto server is running
start-server:
	@if [ ! -f /opt/homebrew/sbin/mosquitto ]; then \
		echo "Installing mosquitto via Homebrew..."; \
		brew install mosquitto; \
	fi

	brew services start mosquitto

start-zigbee:
	@if [ ! -d ~/zigbee2mqtt ]; then \
		echo "Cloning zigbee2mqtt from GitHub..."; \
		git clone --depth 1 https://github.com/Koenkk/zigbee2mqtt.git ~/zigbee2mqtt; \
		cd ~/zigbee2mqtt; \
		npm install; \
	fi
	@ZIGBEE2MQTT_CONFIG_SERIAL_PORT=$$(ls /dev/cu.usbserial-* 2>/dev/null | head -1); \
	if [ -z "$$ZIGBEE2MQTT_CONFIG_SERIAL_PORT" ]; then \
		echo "Warning: No USB serial port found. Please check your device connection."; \
		ZIGBEE2MQTT_CONFIG_SERIAL_PORT="/dev/cu.usbserial-XXXXXX"; \
	fi; \
	cd ~/zigbee2mqtt && ZIGBEE2MQTT_CONFIG_SERIAL_PORT=$$ZIGBEE2MQTT_CONFIG_SERIAL_PORT npm start

listen:
	make start-server
	make start-zigbee

list-devices:
	@echo "Listing all devices..."; \
	@mosquitto_sub -t "zigbee2mqtt/bridge/devices" -C 1 | jq -r '.[] | "\(.friendly_name // .name // "Unknown") - \(.ieee_address) - \(.model_id // "Unknown model")"'

teardown:
	@sudo brew services stop mosquitto
	@killall -9 node

# Deployment operations
build:
	@docker-compose build --no-cache

up:
	@mkdir -p data logs mosquitto/{config,data,log}
	@docker-compose up

build-up:
	@make build
	@make up

build-up-local:
	make build
	make up-local

up-local:
	docker-compose --profile local up

down:
	docker-compose down

open-test-website:
	open http://localhost:5500/core/iot/zigbee/index.html

clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

clean-all:
	docker-compose down -v --remove-orphans --rmi all
	docker system prune -af