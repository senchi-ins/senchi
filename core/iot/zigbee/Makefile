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

subscribe:
	mosquitto_sub -t "zigbee2mqtt/0x00158d008b91088e"

list-devices:
	@echo "Listing all devices..."; \
	@mosquitto_sub -t "zigbee2mqtt/bridge/devices" -C 1 | jq -r '.[] | "\(.friendly_name // .name // "Unknown") - \(.ieee_address) - \(.model_id // "Unknown model")"'

teardown:
	@sudo brew services stop mosquitto
	@killall -9 node