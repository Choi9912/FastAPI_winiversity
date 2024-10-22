from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from ...schemas import user as user_schema
from ...models.user import User
from ...db.session import get_async_db
from ...services.auth_service import AuthService
from ...services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

@router.post("/register", response_model=user_schema.User)
async def register(
    user: user_schema.UserCreate,
    db: AsyncSession = Depends(get_async_db),
    user_service: UserService = Depends()
):
    return await user_service.create_user(db, user)

@router.post("/token", response_model=user_schema.TokenPair)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db),
    auth_service: AuthService = Depends()
):
    return await auth_service.authenticate_user(db, form_data.username, form_data.password)

@router.post("/refresh", response_model=user_schema.Token)
async def refresh_access_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_async_db),
    auth_service: AuthService = Depends()
):
    return await auth_service.refresh_token(db, refresh_token)

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(token: str = Depends(oauth2_scheme)):
    return {"msg": "로그아웃 성공"}