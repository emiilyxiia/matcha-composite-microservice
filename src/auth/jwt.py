from datetime import datetime, timedelta, timezone
from jose import jwt
from src.config import JWT_SECRET, JWT_ALG, JWT_EXPIRE_MINUTES

def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_EXPIRE_MINUTES)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
