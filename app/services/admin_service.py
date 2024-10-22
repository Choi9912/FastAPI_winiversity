from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.user import User
from ..models.courses import Course
from ..schemas import user as user_schema
from ..schemas import courses as course_schema
from fastapi import HTTPException
from typing import List


class AdminService:
    async def get_all_users(self, db: AsyncSession) -> List[User]:
        result = await db.execute(select(User))
        return result.scalars().all()

    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> User:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        return user

    async def update_user(self, db: AsyncSession, user_id: int, user_update: user_schema.UserUpdate) -> User:
        user = await self.get_user_by_id(db, user_id)
        user_data = user_update.model_dump(exclude_unset=True)
        for key, value in user_data.items():
            setattr(user, key, value)
        await db.commit()
        await db.refresh(user)
        return user

    async def delete_user(self, db: AsyncSession, user_id: int) -> None:
        user = await self.get_user_by_id(db, user_id)
        await db.delete(user)
        await db.commit()

    async def create_course(self, db: AsyncSession, course: course_schema.CourseCreate) -> Course:
        new_course = Course(**course.model_dump())
        db.add(new_course)
        await db.commit()
        await db.refresh(new_course)
        return new_course

    async def update_course(self, db: AsyncSession, course_id: int, course_update: course_schema.CourseUpdate) -> Course:
        result = await db.execute(select(Course).where(Course.id == course_id))
        course = result.scalar_one_or_none()
        if not course:
            raise HTTPException(status_code=404, detail="과정을 찾을 수 없습니다.")
        course_data = course_update.model_dump(exclude_unset=True)
        for key, value in course_data.items():
            setattr(course, key, value)
        await db.commit()
        await db.refresh(course)
        return course

    async def delete_course(self, db: AsyncSession, course_id: int) -> None:
        result = await db.execute(select(Course).where(Course.id == course_id))
        course = result.scalar_one_or_none()
        if not course:
            raise HTTPException(status_code=404, detail="과정을 찾을 수 없습니다.")
        await db.delete(course)
        await db.commit()

