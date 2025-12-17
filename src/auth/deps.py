from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.auth.jwt import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)

def require_jwt(creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)):
    if creds is None:
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = creds.credentials  # automatically strips "Bearer "
    return decode_access_token(token)
