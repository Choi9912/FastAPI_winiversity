from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Optional
from ..core import security, config
from ..models.user import User
from ..db.session import get_async_db  # 이 줄을 수정했습니다
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import user_schema  # 이 줄을 수정했습니다

# is_token_blacklisted 함수를 import 하거나 정의해야 합니다
from ..core.security import (
    is_token_blacklisted,
)  # 예시 import 경로, 실제 경로에 맞게 수정하세요


async def get_current_user(
    db: AsyncSession = Depends(get_async_db),
    token: str = Depends(security.oauth2_scheme),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 인증 정보입니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, config.settings.SECRET_KEY, algorithms=[config.settings.ALGORITHM]
        )
        username: Optional[str] = payload.get("sub")
        jti: Optional[str] = payload.get("jti")
        if username is None or jti is None:
            raise credentials_exception
        if is_token_blacklisted(jti):
            raise credentials_exception
        token_data = user_schema.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="비활성화된 사용자입니다.")
    return current_user


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    return current_user


def get_current_admin_user(
    current_user: int = Depends(get_current_user), db: Session = Depends(get_async_db)
):
    user = db.query(User).filter(User.id == current_user).first()
    if not user or user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )
    return user
