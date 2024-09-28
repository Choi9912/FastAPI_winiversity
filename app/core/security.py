from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from ..core.config import settings
import redis

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Redis 클라이언트 설정
redis_client = redis.Redis(host="localhost", port=6379, db=0)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    import uuid

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    jti = str(uuid.uuid4())
    to_encode = {"exp": expire, "sub": str(subject), "jti": jti}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def blacklist_token(jti: str):
    # 토큰의 jti를 블랙리스트에 추가 (예: 1시간 유효)
    redis_client.set(jti, "blacklisted", ex=3600)


def is_token_blacklisted(jti: str) -> bool:
    return redis_client.exists(jti) == 1
