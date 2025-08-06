import logging

from fastapi import APIRouter, Request, Response


logger = logging.getLogger(__name__)

TAG = "SMS"
PREFIX = "/sms"

router = APIRouter()

@router.post("/") # Default route for Twilio to hit
async def reply_sms(request: Request):
    sms_bot = request.app.state.sms_bot
    # Reset response client for new request
    sms_bot.reset_response()
    
    form = await request.form()
    body = form.get('Body')

    if body.lower() == 'hello':
        sms_bot.reply_sms("Hi!")
    elif body.lower() == 'bye':
        sms_bot.reply_sms("Goodbye")
    else:
        # Default response for unrecognized messages
        sms_bot.reply_sms("Thanks for your message!")
    
    logger.info(f"Received SMS: {body}, responding with: {sms_bot.response_client}")

    return Response(
        content=str(sms_bot.response_client),
        media_type="application/xml"
    )

