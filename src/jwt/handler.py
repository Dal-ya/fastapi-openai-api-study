import os
import time
from typing import Dict
import jwt
from dotenv import load_dotenv

load_dotenv()


def token_response(token: str):
    return {
        "access_token": token
    }


def sign_jwt(user_email: str) -> Dict[str, str]:
    payload = {
        'user_email': user_email,
        'expires': time.time() + 2400
    }
    return token_response(jwt.encode(payload, os.environ["JWT_SECRET"], algorithm="HS256"))


def decode_jwt(token: str) -> dict:
    decoded_token = jwt.decode(token.encode(), os.environ["JWT_SECRET"], algorithms=["HS256"])
    return decoded_token if decoded_token['expires'] >= time.time() else {}
