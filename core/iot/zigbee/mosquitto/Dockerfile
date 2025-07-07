FROM eclipse-mosquitto:latest
COPY mosquitto.conf /mosquitto/config/mosquitto.conf
COPY mosquitto_passwd /mosquitto/config/passwd
EXPOSE 1883
CMD ["mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]