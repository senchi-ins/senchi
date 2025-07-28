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

TAG = "Auth"
PREFIX = "/auth"

router = APIRouter()

class VerifyAuthRequest(BaseModel):
    jwt: str

@router.get("/")
async def get_verification():
    return {"message": "verification model activated"}

@router.post("/register")
async def register_user(
    register_request: RegisterRequest,
    request: Request,
) -> TokenResponse:
    """
    Register a new user

    TODO: Add a verification step to the registration process
    """
    email = register_request.email
    password = str(register_request.password)
    full_name = register_request.full_name
    device_serial = register_request.device_serial
    push_token = register_request.push_token

    # TODO: Allow user to configure property name and address on signup
    property_name = "Main"
    address = "123 Main St, Anytown, Ontario"
    first_name, _ = full_name.split(' ', 1)

    # TODO: Make this customizable
    ttl = 3600
    
    # 1. Add a user to zb_users, 2. Add the property to zb_properties, 3. Add the user-property relationship to zb_user_properties
    # 4. Add the device to zb_devices
    try:
        password_hash = hash_password(password)
        user_result = request.app.state.db.insert_user(email, password_hash, full_name)
        user_id = user_result['id'] if user_result else None
        
        property_result = request.app.state.db.insert_property(property_name, address)
        property_id = property_result['id'] if property_result else None
        print(f"property_id: {property_id}")
        
        if user_id and property_id:
            request.app.state.db.insert_user_property_relationship(user_id, property_id, user_id)
            request.app.state.db.insert_user_device(user_id, device_serial, property_id)
        else:
            raise HTTPException(status_code=500, detail="Failed to create user or property")

        # TODO: Also store and set up the push notification token
        # TODO: Verify the push token is valid / available at this point
        request.app.state.redis_db.set_key(f"user:{user_id}:push_token", push_token, ttl=ttl)

        # Used for quick lookup of the topic for the push notification
        location_id = f"rpi-zigbee-{device_serial[-8:]}"
        topic = f"zigbee2mqtt/senchi-{device_serial}/#"
        key = f"user:{user_id}:{location_id}"
        request.app.state.redis_db.set_key(key, topic, ttl=ttl)

        # Store the location id in redis for backwards compatibility
        request.app.state.redis_db.set_key(f"location:{location_id}:users", user_id, ttl=ttl)

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
            location_id=property_id,
            device_serial=device_serial,
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
        logger.error(f"Failed to register user: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")
    
    

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
            user_id, first_name, hashed_password = request.app.state.db.get_hashed_password(email)
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
async def verify_auth(request: Request) -> TokenResponse:
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
    now = datetime.now()
    expires = now + timedelta(hours=int(os.getenv("JWT_EXPIRY_HOURS")))
    device_serial = request.app.state.db.get_device_serial(user_id)
    device_serial = device_serial['serial_number'] if device_serial else None
    print(f"device_serial: {device_serial}")
    if device_serial:
        location_id = f"rpi-zigbee-{device_serial[-8:]}"
    else:
        location_id = None

    user_info = UserInfoResponse(
        user_id=user_id,
        location_id=location_id,
        device_serial=device_serial,
        full_name=None,
        iat=now.timestamp(),
        exp=expires.timestamp(),
        created_at=now.isoformat()
    )

    return TokenResponse(
        jwt_token=token,
        expires_at=expires.isoformat(),
        user_info=user_info,
    )