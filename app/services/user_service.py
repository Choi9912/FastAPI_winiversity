from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from ..models.user import User, UserRole
from ..models.courses import Certificate
from ..schemas import user as user_schema
from fastapi import HTTPException, status
from ..core import security
from ..core.config import settings
import os
from fastapi.responses import FileResponse


class UserService:
    async def update_user(self, db: AsyncSession, current_user: User, user_update: user_schema.UserUpdate):
        if current_user.role != UserRole.STUDENT:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        user_data = user_update.model_dump(exclude_unset=True)
        stmt = update(User).where(User.id == current_user.id).values(**user_data)
        await db.execute(stmt)
        await db.commit()
        await db.refresh(current_user)
        return current_user

    async def delete_user(self, db: AsyncSession, current_user: User):
        if current_user.role != UserRole.STUDENT:
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        stmt = delete(User).where(User.id == current_user.id)
        await db.execute(stmt)
        await db.commit()

    async def create_user(self, db: AsyncSession, user: user_schema.UserCreate) -> User:
        result = await db.execute(select(User).where(User.username == user.username))
        db_user = result.scalar_one_or_none()
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")

        hashed_password = security.get_password_hash(user.password)
        email = user.email if user.email else f"{user.username}@example.com" 
        db_user = User(
            username=user.username,
            email=email,
            hashed_password=hashed_password,
            is_active=user.is_active,
            role=user.role,
            nickname=user.nickname,
            phone_number=user.phone_number or ""  # 빈 문자열을 기본값으로 설정
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    async def get_user_certificates(self, db: AsyncSession, current_user: User):
        result = await db.execute(
            select(Certificate).where(Certificate.user_id == current_user.id)
        )
        return result.scalars().all()

    async def download_certificate(self, db: AsyncSession, current_user: User, certificate_id: int):
        result = await db.execute(
            select(Certificate).where(
                Certificate.id == certificate_id, Certificate.user_id == current_user.id
            )
        )
        certificate = result.scalar_one_or_none()
        if not certificate:
            raise HTTPException(status_code=404, detail="Certificate not found")

        pdf_filename = f"certificate_{certificate_id}.pdf"
        pdf_path = os.path.join(settings.CERTIFICATE_DIR, pdf_filename)

        if not os.path.exists(pdf_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate file not found. It may still be generating.",
            )

        return FileResponse(pdf_path, filename=pdf_filename, media_type="application/pdf")

    async def get_user_credits(self, current_user: User):
        return current_user.credits

    async def get_user_learning_time(self, current_user: User):
        return current_user.total_learning_time

    async def get_course_valid_until(self, current_user: User):
        if not current_user.course_valid_until:
            raise HTTPException(status_code=404, detail="No active course subscription")
        return current_user.course_valid_until
