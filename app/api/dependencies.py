from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from ..core import security, config
from ..models.user import User, UserRole
from ..db.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import user_schema
from ..core.security import is_token_blacklisted
from sqlalchemy.future import select
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# get_current_user 함수 업데이트
async def get_current_user(
    token: str = Depends(security.oauth2_scheme),
    db: AsyncSession = Depends(get_async_db),
):
    logger.debug(f"Received token: {token}")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 인증 정보입니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, config.settings.SECRET_KEY, algorithms=[config.settings.ALGORITHM]
        )
        logger.debug(f"Decoded payload: {payload}")
        username: Optional[str] = payload.get("sub")
        jti: Optional[str] = payload.get("jti")
        if username is None:
            logger.error("Username not found in token")
            raise credentials_exception
        if jti is not None and is_token_blacklisted(jti):
            logger.error("Token is blacklisted")
            raise credentials_exception
        token_data = user_schema.TokenData(username=username)
    except JWTError as e:
        logger.error(f"JWT Error: {str(e)}")
        raise credentials_exception

    logger.debug(f"Looking up user: {username}")
    async with db as session:
        query = select(User).filter(User.username == token_data.username)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

    if user is None:
        logger.error(f"User not found: {username}")
        raise credentials_exception
    logger.debug(f"User authenticated: {username}")
    return user


# get_current_active_user 함수 업데이트
async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="비활성화된 사용자입니다.")
    return current_user


async def admin_required(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user
