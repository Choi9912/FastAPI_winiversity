from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from ..core import security, config
from ..models.user import User, UserRole
from ..db.session import get_async_db  # 이 줄을 수정했습니다
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import user_schema  # 이 줄을 수정했습니다
from ..core.security import is_token_blacklisted
from sqlalchemy.future import select


# get_current_user 함수 업데이트
async def get_current_user(
    token: str = Depends(security.oauth2_scheme),
    db: AsyncSession = Depends(get_async_db),
):
    print(f"Received token: {token}")  # 디버깅 로그
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

    # 비동기 쿼리 실행
    async with db as session:
        query = select(User).filter(User.username == token_data.username)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    return user


# get_current_active_user 함수 업데이트
def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> Annotated[User, Depends()]:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="비활성화된 사용자입니다.")
    return current_user


# require_admin 함수 업데이트
def require_admin(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> Annotated[User, Depends()]:
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
    return current_user


# get_current_admin_user 함수 업데이트
def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> Annotated[User, Depends()]:
    user = db.query(User).filter(User.id == current_user).first()
    if not user or user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )
    return user


async def admin_required(current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user
