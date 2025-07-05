import paho.mqtt.client as mqtt
client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.loop_start()
print(client.connected_flag)

client.publish("zigbee2mqtt/bridge/health", "test")
print("Published test message")
client.loop_stop()
client.disconnect()