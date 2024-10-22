from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime
from ...schemas import user as user_schema
from ...models.user import User, UserRole
from ...db.session import get_async_db
from ...api.dependencies import get_current_active_user
from ...services.user_service import UserService
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_active_user)],
)

@router.get("/me", response_model=user_schema.User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.put("/me", response_model=user_schema.User)
async def update_user_profile(
    user_update: user_schema.UserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends()
):
    return await user_service.update_user(db, current_user, user_update)

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends()
):
    await user_service.delete_user(db, current_user)


@router.get("/me/certificates", response_model=List[user_schema.Certificate])
async def get_user_certificates(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends()
):
    return await user_service.get_user_certificates(db, current_user)

@router.get("/me/certificates/{certificate_id}/download")
async def download_certificate(
    certificate_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends()
):
    return await user_service.download_certificate(db, current_user, certificate_id)

@router.get("/me/credits", response_model=int)
async def get_user_credits(
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends()
):
    return await user_service.get_user_credits(current_user)

@router.get("/me/learning_time", response_model=int)
async def get_user_learning_time(
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends()
):
    return await user_service