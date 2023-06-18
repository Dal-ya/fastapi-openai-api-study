from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .handler import decode_jwt


def verify_jwt(token: str) -> bool:
    is_token_valid: bool = False

    payload = decode_jwt(token)
    if payload:
        is_token_valid = True
    return is_token_valid


class JWTBearer(HTTPBearer):

    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        print("Credentials :", credentials)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication token")

            if not verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token")

            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization token")
