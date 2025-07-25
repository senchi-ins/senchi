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

from schemas.auth import TokenRequest, TokenResponse, LoginRequest, UserInfoResponse


logger = logging.getLogger(__name__)

TAG = "Auth"
PREFIX = "/auth"

router = APIRouter()

class VerifyAuthRequest(BaseModel):
    jwt: str

@router.get("/")
async def get_verification():
    return {"message": "verification model activated"}

# TODO: Make this a util function and make this endpoint auth/login using email and password
@router.post("/login")
async def create_user_token(
    login_request: LoginRequest,
    request: Request,
    push_token: Optional[str] = None, # TODO: Is this needed?
    # refresh_token: Optional[str] = None, # TODO: Add refresh token to the payload rather than using a password
) -> TokenResponse:
        """Create JWT token for a user during device setup
        
        Note: This version differs from the iot branch because we are not using the device serial to create the token.
        This is explicitly for the user to login AFTER initial setup.

        TODO: Consolidate the server into a monolith to simplify the codebase
        """
        email = login_request.email
        password = str(login_request.password)
        try:
            user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, email))

            first_name, hashed_password = request.app.state.db.get_hashed_password(email)
            if not hashed_password:
                raise HTTPException(status_code=404, detail="User not found, please create an account")
            
            verified = verify_password(password, hashed_password)
            if not verified:
                raise HTTPException(status_code=401, detail="Invalid password")
            
            now = datetime.now()
            expires = now + timedelta(hours=int(os.getenv("JWT_EXPIRY_HOURS")))
            
            jwt_payload = {
                "user_id": user_id,
                "email": email,
                "push_token": push_token,
                "iat": now.timestamp(),
                "exp": expires.timestamp()
            }
            
            jwt_token = jwt.encode(jwt_payload, os.getenv("JWT_SECRET"), algorithm=os.getenv("JWT_ALGORITHM"))

            user_info = UserInfoResponse(
                user_id=user_id,
                location_id=None, # TODO: Add location_id
                device_serial=None, # TODO: Add device_serial
                full_name=first_name,
                iat=now.timestamp(),
                exp=expires.timestamp(),
                created_at=now.isoformat()
            )
            return TokenResponse(
                jwt_token=jwt_token,
                expires_at=expires.isoformat(),
                user_info=user_info,
            )
            
        except Exception as e:
            logger.error(f"Failed to create user token: {e}")
            raise HTTPException(status_code=500, detail="Token creation failed")

@router.post("/verify")
async def verify_auth(request: Request):
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        logger.error("Authorization header missing")
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            logger.error("Invalid authentication scheme")
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        logger.error("Invalid authorization header format")
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    try:
        decoded_jwt = decode_jwt(token)
        logger.info(f"Decoded JWT: {decoded_jwt}")
    except jwt.InvalidTokenError:
        logger.error("Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = decoded_jwt["user_id"]

    return {"message": "verification model activated"}