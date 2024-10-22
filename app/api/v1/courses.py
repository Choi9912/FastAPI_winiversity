from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ...db.session import get_async_db
from ...models.user import User
from ...api.dependencies import get_current_active_user
from ...services.course_service import CourseService
from ...schemas import courses as course_schema
from typing import List

router = APIRouter(prefix="/courses", tags=["courses"])

@router.get("/", response_model=List[course_schema.CourseInDB])
async def get_all_courses(
    db: AsyncSession = Depends(get_async_db),
    course_service: CourseService = Depends()
):
    return await course_service.get_all_courses(db)

@router.get("/roadmap", response_model=List[course_schema.CourseRoadmap])
async def get_course_roadmap(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
    course_service: CourseService = Depends()
):
    return await course_service.get_course_roadmap(db, current_user.id)

@router.post("/{course_id}/enroll", response_model=course_schema.Enrollment)
async def enroll_course(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
    course_service: CourseService = Depends()
):
    return await course_service.enroll_course(db, current_user.id, course_id)

@router.post("/", response_model=course_schema.CourseInDB, status_code=status.HTTP_201_CREATED)
async def create_course(
    course: course_schema.CourseCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    course_service: CourseService = Depends()
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only administrators can create courses")
    return await course_service.create_course(db, course)

@router.get("/{course_id}", response_model=course_schema.CourseInDB)
async def get_course(
    course_id: int,
    db: AsyncSession = Depends(get_async_db),
    course_service: CourseService = Depends()
):
    return await course_service.get_course(db, course_id)

@router.post("/{course_id}/lessons", response_model=course_schema.LessonInDB)
async def add_lesson_to_course(
    course_id: int,
    lesson: course_schema.LessonCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    course_service: CourseService = Depends()
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only administrators can add lessons")
    return await course_service.add_lesson_to_course(db, course_id, lesson)

@router.put("/{course_id}/lessons/{lesson_id}", response_model=course_schema.LessonInDB)
async def update_lesson(
    course_id: int,
    lesson_id: int,
    lesson_update: course_schema.LessonUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    course_service: CourseService = Depends()
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only administrators can update lessons")
    return await course_service.update_lesson(db, lesson_id, lesson_update)

@router.delete("/{course_id}/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    course_id: int,
    lesson_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    course_service: CourseService = Depends()
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only administrators can delete lessons")
    await course_service.delete_lesson(db, lesson_id)

@router.post("/{course_id}/lessons/{lesson_id}/progress", response_model=course_schema.LessonProgressInDB)
async def update_lesson_progress(
    course_id: int,
    lesson_id: int,
    progress: course_schema.LessonProgressUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    course_service: CourseService = Depends()
):
    return await course_service.update_lesson_progress(db, lesson_id, current_user.id, progress)

@router.get("/{course_id}/lessons/{lesson_id}/progress", response_model=course_schema.LessonProgressInDB)
async def get_lesson_progress(
    course_id: int,
    lesson_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    course_service: CourseService = Depends()
):
    return await course_service.get_lesson_progress(db, lesson_id, current_user.id)

@router.get("/{course_id}/lessons/{lesson_id}", response_model=course_schema.LessonInDB)
async def get_lesson(
    course_id: int,
    lesson_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    course_service: CourseService = Depends()
):
    return await course_service.get_lesson(db, course_id, lesson_id)