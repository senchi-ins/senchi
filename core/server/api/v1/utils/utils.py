import os
import jwt
import base64
from passlib.context import CryptContext
from fastapi import HTTPException


def decode_jwt(jwt_token: str) -> dict:
    try:
        decoded_jwt = jwt.decode(jwt_token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        return decoded_jwt
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password, rounds=12)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

