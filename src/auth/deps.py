from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.auth.jwt import decode_access_token

bearer_scheme = HTTPBearer()

def require_jwt(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    token = creds.credentials
    return decode_access_token(token)
