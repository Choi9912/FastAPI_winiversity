from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ...schemas import courses as course_schema
from ...models.courses import Course, Lesson, LessonStep, Enrollment, LessonProgress
from ...models.user import User
from ...db.session import get_async_db
from ...api.dependencies import get_current_active_user
from sqlalchemy import select, insert, update, delete

router = APIRouter(
    prefix="/courses",
    tags=["courses"],
)


@router.get("/", response_model=List[course_schema.CourseInDB])
async def get_all_courses(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Course).order_by(Course.order))
    courses = result.scalars().all()
    return courses


@router.get("/roadmap", response_model=List[course_schema.CourseRoadmap])
async def get_course_roadmap(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    courses_result = await db.execute(select(Course).order_by(Course.order))
    courses = courses_result.scalars().all()

    enrollments_result = await db.execute(
        select(Enrollment).where(Enrollment.user_id == current_user.id)
    )
    user_enrollments = enrollments_result.scalars().all()
    enrolled_course_ids = {enrollment.course_id for enrollment in user_enrollments}

    roadmap = []
    for course in courses:
        course_data = course_schema.CourseRoadmap.from_orm(course)
        course_data.is_enrolled = course.id in enrolled_course_ids
        roadmap.append(course_data)

    return roadmap


@router.post("/enroll/{course_id}", response_model=course_schema.Enrollment)
async def enroll_course(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    course_result = await db.execute(select(Course).where(Course.id == course_id))
    course = course_result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="과목을 찾을 수 없습니다.")

    existing_enrollment_result = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == current_user.id, Enrollment.course_id == course_id
        )
    )
    existing_enrollment = existing_enrollment_result.scalar_one_or_none()

    if existing_enrollment:
        raise HTTPException(status_code=400, detail="이미 등록된 과목입니다.")

    new_enrollment = Enrollment(user_id=current_user.id, course_id=course_id)
    db.add(new_enrollment)
    await db.commit()
    await db.refresh(new_enrollment)

    return new_enrollment


@router.post(
    "/", response_model=course_schema.CourseInDB, status_code=status.HTTP_201_CREATED
)
async def create_course(
    course: course_schema.CourseCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create courses",
        )

    new_course = Course(**course.dict(exclude={"lessons"}))
    if new_course.is_paid and new_course.price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Paid courses must have a price greater than 0",
        )

    db.add(new_course)
    await db.flush()

    for lesson_data in course.lessons:
        new_lesson = Lesson(
            **lesson_data.dict(exclude={"steps"}), course_id=new_course.id
        )
        db.add(new_lesson)
        await db.flush()

        for step_data in lesson_data.steps:
            new_step = LessonStep(**step_data.dict(), lesson_id=new_lesson.id)
            db.add(new_step)

    await db.commit()
    await db.refresh(new_course)
    return new_course


@router.get("/{course_id}", response_model=course_schema.CourseInDB)
async def get_course(course_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/{course_id}/lessons/", response_model=course_schema.LessonInDB)
async def add_lesson_to_course(
    course_id: int,
    lesson: course_schema.LessonCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403, detail="Only administrators can add lessons"
        )

    course_result = await db.execute(select(Course).where(Course.id == course_id))
    course = course_result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    new_lesson = Lesson(**lesson.dict(exclude={"steps"}), course_id=course_id)
    db.add(new_lesson)
    await db.flush()

    for step_data in lesson.steps:
        new_step = LessonStep(**step_data.dict(), lesson_id=new_lesson.id)
        db.add(new_step)

    await db.commit()
    await db.refresh(new_lesson)
    return new_lesson


@router.put("/lessons/{lesson_id}", response_model=course_schema.LessonInDB)
async def update_lesson(
    lesson_id: int,
    lesson_update: course_schema.LessonUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403, detail="Only administrators can update lessons"
        )

    lesson_result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    existing_lesson = lesson_result.scalar_one_or_none()
    if not existing_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    for key, value in lesson_update.dict(exclude_unset=True).items():
        setattr(existing_lesson, key, value)

    await db.commit()
    await db.refresh(existing_lesson)
    return existing_lesson


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    lesson_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403, detail="Only administrators can delete lessons"
        )

    lesson_result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = lesson_result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    await db.execute(delete(Lesson).where(Lesson.id == lesson_id))
    await db.commit()
    return


@router.post(
    "/lessons/{lesson_id}/progress", response_model=course_schema.LessonProgressInDB
)
async def update_lesson_progress(
    lesson_id: int,
    progress: course_schema.LessonProgressUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    lesson_progress_result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.lesson_id == lesson_id,
            LessonProgress.user_id == current_user.id,
        )
    )
    lesson_progress = lesson_progress_result.scalar_one_or_none()

    if not lesson_progress:
        lesson_progress = LessonProgress(lesson_id=lesson_id, user_id=current_user.id)
        db.add(lesson_progress)

    lesson_progress.last_watched_position = progress.last_watched_position
    lesson_progress.is_completed = progress.is_completed

    await db.commit()
    await db.refresh(lesson_progress)
    return lesson_progress


@router.get(
    "/lessons/{lesson_id}/progress", response_model=course_schema.LessonProgressInDB
)
async def get_lesson_progress(
    lesson_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    lesson_progress_result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.lesson_id == lesson_id,
            LessonProgress.user_id == current_user.id,
        )
    )
    lesson_progress = lesson_progress_result.scalar_one_or_none()

    if not lesson_progress:
        raise HTTPException(status_code=404, detail="Progress not found")
    return lesson_progress
