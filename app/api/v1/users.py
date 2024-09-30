from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ...schemas import user as user_schema
from ...models.user import User, UserRole
from ...core import security
from ...db.session import get_async_db
from ...api.dependencies import get_current_active_user
from sqlalchemy import select, update, delete

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
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    user_data = user_update.dict(exclude_unset=True)

    stmt = update(User).where(User.id == current_user.id).values(**user_data)
    await db.execute(stmt)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    stmt = delete(User).where(User.id == current_user.id)
    await db.execute(stmt)
    await db.commit()
    return


@router.post("/", response_model=user_schema.User)
async def create_user(
    user: user_schema.UserCreate, db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(select(User).where(User.username == user.username))
    db_user = result.scalar_one_or_none()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = security.get_password_hash(user.password)
    db_user = User(
        username=user.username,
        hashed_password=hashed_password,
        is_active=user.is_active,
        role=user.role,
        nickname=user.nickname,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
