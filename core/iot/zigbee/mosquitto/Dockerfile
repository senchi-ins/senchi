FROM eclipse-mosquitto:latest

# TODO: Update to use uv
RUN apk add --no-cache \
    python3 \
    py3-pip \
    supervisor

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install fastapi uvicorn python-multipart

COPY mosquitto.conf /mosquitto/config/mosquitto.conf
COPY mosquitto_passwd /mosquitto/config/passwd

COPY user_manager.py /usr/local/bin/user_manager.py

RUN mkdir -p /etc/supervisor/conf.d
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN chmod 600 /mosquitto/config/passwd
RUN chmod +x /usr/local/bin/user_manager.py

EXPOSE 1883 8001

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]