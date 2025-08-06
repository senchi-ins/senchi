import os
import asyncio
import hashlib
import jwt
import logging
import uuid
from datetime import datetime, timedelta

from server.api.v1.utils.utils import decode_jwt, hash_password, verify_password
from fastapi import APIRouter, HTTPException, Depends, Body, Request
from typing import List, Optional
from pydantic import BaseModel

from schemas.auth import (
    TokenResponse,
    LoginRequest,
    UserInfoResponse,
    RegisterRequest
)


logger = logging.getLogger(__name__)

TAG = "SMS"
PREFIX = "/sms"

router = APIRouter()

@router.post("/") # Default route for Twilio to hit
async def reply_sms(request: Request):
    sms_bot = request.app.state.sms_bot
    form = await request.form()
    body = form.get('Body')

    if body == 'hello':
        sms_bot.reply_sms("Hi!")
    elif body == 'bye':
        sms_bot.reply_sms("Goodbye")
    return str(sms_bot.response_client)

