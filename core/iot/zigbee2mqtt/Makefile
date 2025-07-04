# Ensure the mosquitto server is running
start-server:
	# Ensure the mosquitto server is runnin
	# Check if mosquitto is installed
	if ! command -v mosquitto &> /dev/null; then
		brew install mosquitto # Assuming you're using Homebrew
	fi

	# Start the mosquitto server
	mosquitto -c /etc/mosquitto/mosquitto.conf

start-zigbee2mqtt:
	# Check if zigbee2mqtt source code exists
	if [ ! -d ~/zigbee2mqtt ]; then
		echo "Cloning zigbee2mqtt from GitHub..."
		git clone --depth 1 https://github.com/Koenkk/zigbee2mqtt.git ~/zigbee2mqtt
		cd ~/zigbee2mqtt
		npm install

	fi

	touch /data/configuration.yaml
	
	# Find the USB serial port
	SERIAL_PORT=$$(ls /dev/cu.usbserial-* 2>/dev/null | head -1)
	if [ -z "$$SERIAL_PORT" ]; then
		echo "Warning: No USB serial port found. Please check your device connection."
		SERIAL_PORT="/dev/cu.usbserial-XXXXXX"
	fi
	
	# Write configuration to the file
	cat > /data/configuration.yaml << EOF
serial:
  port: $$SERIAL_PORT
  adapter: zigate  # Important: Third Reality uses zigate protocol

mqtt:
  server: mqtt://localhost:1883

advanced:
  channel: 11  # Change if needed to avoid WiFi interference
EOF

	npm start

start-all:
	make start-server
	make start-zigbee2mqtt

teardown:
	killall -9 mosquitto
	killall -9 node