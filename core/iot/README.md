# Running the webhook server

Webhook servers cannot be run locally, so we need to use a service like ngrok to
forward the requests to our local server. This is a bit of a pain, so everthing is
compiled into a single makefile

```bash
make start-ngrok

# Mew terminal
make start-server

# New terminal
make start-monitoring
```

This will start the ngrok server and the webhook server. The ngrok server will
forward the requests to the webhook server. The webhook server will print the
requests to the console.

The webhook server will also update the webhook config with the new ngrok URL.

## Notes:

The server will get alerts only when the devices state changes (i.e. when a leak
is detected). A `detection_state` of `1` indicates a leak, `0` indicates no leak.