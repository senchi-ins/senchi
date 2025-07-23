import os
import jwt
from fastapi import HTTPException


def decode_jwt(jwt_token: str) -> dict:
    try:
        decoded_jwt = jwt.decode(jwt_token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        return decoded_jwt
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")