from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.courses import Course, Enrollment, Lesson, LessonProgress
from ..schemas import courses as course_schema
from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from typing import List


class CourseService:
    async def get_all_courses(self, db: AsyncSession) -> List[Course]:
        result = await db.execute(
            select(Course)
            .options(selectinload(Course.lessons).selectinload(Lesson.steps))
            .order_by(Course.order)
        )
        return result.scalars().all()

    async def get_course_roadmap(self, db: AsyncSession, user_id: int) -> List[course_schema.CourseRoadmap]:
        courses_result = await db.execute(
            select(Course).options(selectinload(Course.lessons)).order_by(Course.order)
        )
        courses = courses_result.scalars().all()

        enrollments_result = await db.execute(
            select(Enrollment).where(Enrollment.user_id == user_id)
        )
        user_enrollments = enrollments_result.scalars().all()
        enrolled_course_ids = {enrollment.course_id for enrollment in user_enrollments}

        roadmap = []
        for course in courses:
            course_data = course_schema.CourseRoadmap.from_orm(course)
            course_data.is_enrolled = course.id in enrolled_course_ids
            roadmap.append(course_data)

        return roadmap

    async def enroll_course(self, db: AsyncSession, user_id: int, course_id: int) -> Enrollment:
        course_result = await db.execute(select(Course).where(Course.id == course_id))
        course = course_result.scalar_one_or_none()
        if not course:
            raise HTTPException(status_code=404, detail="과목을 찾을 수 없습니다.")

        existing_enrollment_result = await db.execute(
            select(Enrollment).where(
                Enrollment.user_id == user_id, Enrollment.course_id == course_id
            )
        )
        existing_enrollment = existing_enrollment_result.scalar_one_or_none()

        if existing_enrollment:
            raise HTTPException(status_code=400, detail="이미 등록된 과목입니다.")

        new_enrollment = Enrollment(user_id=user_id, course_id=course_id)
        db.add(new_enrollment)
        await db.commit()
        await db.refresh(new_enrollment)

        return new_enrollment

    async def create_course(self, db: AsyncSession, course: course_schema.CourseCreate) -> Course:
        new_course = Course(**course.model_dump(exclude={"lessons"}))
        if new_course.is_paid and new_course.price <= 0:
            raise HTTPException(
                status_code=400,
                detail="Paid courses must have a price greater than 0",
            )

        db.add(new_course)
        await db.flush()

        for lesson_data in course.lessons:
            new_lesson = Lesson(
                **lesson_data.model_dump(exclude={"steps"}), course_id=new_course.id
            )
            db.add(new_lesson)
            await db.flush()

            for step_data in lesson_data.steps:
                new_step = LessonStep(**step_data.dict(), lesson_id=new_lesson.id)
                db.add(new_step)

        await db.commit()
        await db.refresh(new_course)

        return new_course

    async def get_course(self, db: AsyncSession, course_id: int) -> Course:
        result = await db.execute(
            select(Course)
            .options(selectinload(Course.lessons).selectinload(Lesson.steps))
            .where(Course.id == course_id)
        )
        course = result.scalar_one_or_none()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        return course

    async def add_lesson_to_course(self, db: AsyncSession, course_id: int, lesson: course_schema.LessonCreate) -> Lesson:
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

    async def update_lesson(self, db: AsyncSession, lesson_id: int, lesson_update: course_schema.LessonUpdate) -> Lesson:
        lesson_result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
        existing_lesson = lesson_result.scalar_one_or_none()
        if not existing_lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")

        for key, value in lesson_update.dict(exclude_unset=True).items():
            setattr(existing_lesson, key, value)

        await db.commit()
        await db.refresh(existing_lesson)
        return existing_lesson

    async def delete_lesson(self, db: AsyncSession, lesson_id: int):
        lesson_result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
        lesson = lesson_result.scalar_one_or_none()
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")

        await db.execute(delete(Lesson).where(Lesson.id == lesson_id))
        await db.commit()

    async def update_lesson_progress(self, db: AsyncSession, lesson_id: int, user_id: int, progress: course_schema.LessonProgressUpdate) -> LessonProgress:
        lesson_progress_result = await db.execute(
            select(LessonProgress).where(
                LessonProgress.lesson_id == lesson_id,
                LessonProgress.user_id == user_id,
            )
        )
        lesson_progress = lesson_progress_result.scalar_one_or_none()

        if not lesson_progress:
            lesson_progress = LessonProgress(lesson_id=lesson_id, user_id=user_id)
            db.add(lesson_progress)

        lesson_progress.last_watched_position = progress.last_watched_position
        lesson_progress.is_completed = progress.is_completed

        await db.commit()
        await db.refresh(lesson_progress)
        return lesson_progress

    async def get_lesson_progress(self, db: AsyncSession, lesson_id: int, user_id: int) -> LessonProgress:
        lesson_progress_result = await db.execute(
            select(LessonProgress).where(
                LessonProgress.lesson_id == lesson_id,
                LessonProgress.user_id == user_id,
            )
        )
        lesson_progress = lesson_progress_result.scalar_one_or_none()

        if not lesson_progress:
            raise HTTPException(status_code=404, detail="Progress not found")
        return lesson_progress

    async def get_lesson(self, db: AsyncSession, course_id: int, lesson_id: int) -> Lesson:
        lesson_result = await db.execute(
            select(Lesson)
            .options(selectinload(Lesson.steps))
            .where(Lesson.id == lesson_id, Lesson.course_id == course_id)
        )
        lesson = lesson_result.scalar_one_or_none()
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        return lesson
