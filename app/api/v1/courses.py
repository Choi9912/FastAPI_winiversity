from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...schemas import courses as course_schema
from ...models.courses import Course, Lesson, LessonStep, Enrollment
from ...models.user import User
from ...db.session import get_db
from ...api.dependencies import get_current_active_user

router = APIRouter(
    prefix="/courses",
    tags=["courses"],
)


@router.get("/", response_model=List[course_schema.CourseInDB])
def get_all_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).order_by(Course.order).all()
    return courses


@router.get("/roadmap", response_model=List[course_schema.CourseRoadmap])
def get_course_roadmap(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    courses = db.query(Course).order_by(Course.order).all()
    user_enrollments = (
        db.query(Enrollment).filter(Enrollment.user_id == current_user.id).all()
    )
    enrolled_course_ids = {enrollment.course_id for enrollment in user_enrollments}

    roadmap = []
    for course in courses:
        course_data = course_schema.CourseRoadmap.from_orm(course)
        course_data.is_enrolled = course.id in enrolled_course_ids
        roadmap.append(course_data)

    return roadmap


@router.post("/enroll/{course_id}", response_model=course_schema.Enrollment)
def enroll_course(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="과목을 찾을 수 없습니다.")

    existing_enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.user_id == current_user.id, Enrollment.course_id == course_id
        )
        .first()
    )

    if existing_enrollment:
        raise HTTPException(status_code=400, detail="이미 등록된 과목입니다.")

    new_enrollment = Enrollment(user_id=current_user.id, course_id=course_id)
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)

    return new_enrollment


@router.post(
    "/", response_model=course_schema.CourseInDB, status_code=status.HTTP_201_CREATED
)
def create_course(
    course: course_schema.CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "admin":
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
    db.flush()

    for lesson_data in course.lessons:
        new_lesson = Lesson(
            **lesson_data.dict(exclude={"steps"}), course_id=new_course.id
        )
        db.add(new_lesson)
        db.flush()

        for step_data in lesson_data.steps:
            new_step = LessonStep(**step_data.dict(), lesson_id=new_lesson.id)
            db.add(new_step)

    db.commit()
    db.refresh(new_course)
    return new_course


@router.get("/{course_id}", response_model=course_schema.CourseInDB)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/{course_id}/lessons/", response_model=course_schema.LessonInDB)
def add_lesson_to_course(
    course_id: int,
    lesson: course_schema.LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403, detail="Only administrators can add lessons"
        )

    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    new_lesson = Lesson(**lesson.dict(exclude={"steps"}), course_id=course_id)
    db.add(new_lesson)
    db.flush()

    for step_data in lesson.steps:
        new_step = LessonStep(**step_data.dict(), lesson_id=new_lesson.id)
        db.add(new_step)

    db.commit()
    db.refresh(new_lesson)
    return new_lesson


@router.put("/lessons/{lesson_id}", response_model=course_schema.LessonInDB)
def update_lesson(
    lesson_id: int,
    lesson_update: course_schema.LessonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403, detail="Only administrators can update lessons"
        )

    existing_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not existing_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    for key, value in lesson_update.dict(exclude_unset=True).items():
        setattr(existing_lesson, key, value)

    db.commit()
    db.refresh(existing_lesson)
    return existing_lesson


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403, detail="Only administrators can delete lessons"
        )

    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    db.delete(lesson)
    db.commit()
    return
