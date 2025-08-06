import os
from dotenv import load_dotenv

from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

load_dotenv()

class MessageBot:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.client = Client(self.account_sid, self.auth_token)
        self.response_client = MessagingResponse()

    def send_sms(self, message, to_number):
        if not to_number:
            to_number = self.from_number
        message = self.client.messages.create(
            messaging_service_sid=os.getenv("TWILIO_MESSAGING_SERVICE_SID"),
            body=message,
            to=to_number
        )
        return message.sid
    
    def reply_sms(self, message, to_number=None):
        success = self.response_client.message(message)
        return success
    
    def reset_response(self):
        self.response_client = MessagingResponse()
