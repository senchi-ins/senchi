import os

from load_dotenv import load_dotenv

load_dotenv()

from twilio.rest import Client

client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

message = client.messages.create(
    to=os.getenv("TWILIO_TO_NUMBER"),
    from_=os.getenv("TWILIO_FROM_NUMBER"),
    body="Hello, world!")