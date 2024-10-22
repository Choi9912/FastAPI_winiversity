from datetime import timedelta, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.user import User
from ..schemas import user as user_schema
from ..core import config
from ..core.security import verify_password, create_access_token, create_refresh_token, decode_token
from fastapi import HTTPException, status

class AuthService:
    async def authenticate_user(self, db: AsyncSession, username: str, password: str) -> user_schema.TokenPair:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자 이름이나 비밀번호가 틀렸습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user.last_login = datetime.utcnow()
        await db.commit()

        access_token_expires = timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=config.settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = create_access_token(
            subject=user.username, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            subject=user.username, expires_delta=refresh_token_expires
        )
        
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

    async def refresh_token(self, db: AsyncSession, refresh_token: str) -> user_schema.Token:
        try:
            payload = decode_token(refresh_token)
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=401, detail="Invalid refresh token")
        except:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        access_token_expires = timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user.username, expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}