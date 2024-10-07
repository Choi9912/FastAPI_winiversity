import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime

from app.models.courses import Certificate
from ...schemas import user as user_schema
from ...models.user import User, UserRole
from ...core import security
from ...db.session import get_async_db
from ...api.dependencies import get_current_active_user
from ...core.config import settings
from sqlalchemy import select, update, delete
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
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    user_data = user_update.model_dump(exclude_unset=True)  

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


@router.get("/me/certificates", response_model=List[user_schema.Certificate])
async def get_user_certificates(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Certificate).where(Certificate.user_id == current_user.id)
    )
    certificates = result.scalars().all()
    return certificates


@router.get("/me/certificates/{certificate_id}/download")
async def download_certificate(
    certificate_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Certificate).where(
            Certificate.id == certificate_id, Certificate.user_id == current_user.id
        )
    )
    certificate = result.scalar_one_or_none()
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")

    # 생성된 PDF 파일의 경로를 구성
    pdf_filename = f"certificate_{certificate_id}.pdf"
    pdf_path = os.path.join(settings.CERTIFICATE_DIR, pdf_filename)

    # 파일이 존재하는지 확인
    if not os.path.exists(pdf_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate file not found. It may still be generating.",
        )

    return FileResponse(pdf_path, filename=pdf_filename, media_type="application/pdf")


@router.get("/me/credits", response_model=int)
async def get_user_credits(current_user: User = Depends(get_current_active_user)):
    return current_user.credits


@router.get("/me/learning_time", response_model=int)
async def get_user_learning_time(current_user: User = Depends(get_current_active_user)):
    return current_user.total_learning_time


@router.get("/me/course_valid_until", response_model=datetime)
async def get_course_valid_until(current_user: User = Depends(get_current_active_user)):
    if not current_user.course_valid_until:
        raise HTTPException(status_code=404, detail="No active course subscription")
    return current_user.course_valid_until


@router.put("/me", response_model=user_schema.User)
async def update_user_me(
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
