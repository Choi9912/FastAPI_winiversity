from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ...schemas import user as user_schema
from ...schemas import courses as course_schema
from ...models.user import User
from ...db.session import get_async_db
from ...api.dependencies import admin_required
from ...services.admin_service import AdminService

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(admin_required)],  # 모든 admin 라우트에 admin_required 의존성 적용
)

@router.get("/users", response_model=List[user_schema.User])
async def get_all_users(
    db: AsyncSession = Depends(get_async_db),
    admin_service: AdminService = Depends()
):
    return await admin_service.get_all_users(db)

@router.get("/users/{user_id}", response_model=user_schema.User)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    admin_service: AdminService = Depends()
):
    return await admin_service.get_user_by_id(db, user_id)

@router.put("/users/{user_id}", response_model=user_schema.User)
async def update_user(
    user_id: int,
    user_update: user_schema.UserUpdate,
    db: AsyncSession = Depends(get_async_db),
    admin_service: AdminService = Depends()
):
    return await admin_service.update_user(db, user_id, user_update)

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    admin_service: AdminService = Depends()
):
    await admin_service.delete_user(db, user_id)

@router.post("/courses", response_model=course_schema.CourseInDB)
async def create_course(
    course: course_schema.CourseCreate,
    db: AsyncSession = Depends(get_async_db),
    admin_service: AdminService = Depends()
):
    return await admin_service.create_course(db, course)

@router.put("/courses/{course_id}", response_model=course_schema.CourseInDB)
async def update_course(
    course_id: int,
    course_update: course_schema.CourseUpdate,
    db: AsyncSession = Depends(get_async_db),
    admin_service: AdminService = Depends()
):
    return await admin_service.update_course(db, course_id, course_update)

@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_async_db),
    admin_service: AdminService = Depends()
):
    await admin_service.delete_course(db, course_id)
