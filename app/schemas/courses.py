from pydantic import BaseModel
from typing import List, Optional


# LessonStep 관련 스키마
class LessonStepBase(BaseModel):
    title: str
    content: str
    order: int


class LessonStepCreate(LessonStepBase):
    pass


class LessonStepInDB(LessonStepBase):
    id: int
    lesson_id: int

    class Config:
        orm_mode = True


# Lesson 관련 스키마
class LessonBase(BaseModel):
    title: str
    content: str
    order: int


class LessonCreate(LessonBase):
    steps: List[LessonStepCreate]


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    order: Optional[int] = None
    steps: Optional[List[LessonStepCreate]] = None


class LessonInDB(LessonBase):
    id: int
    course_id: int
    steps: List[LessonStepInDB]

    class Config:
        orm_mode = True


# Course 관련 스키마
class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    order: int
    is_paid: bool = False
    price: float = 0.0  # 가격 필드 추가


class CourseCreate(CourseBase):
    lessons: List[LessonCreate]


class CourseInDB(CourseBase):
    id: int
    lessons: List[LessonInDB]

    class Config:
        orm_mode = True


class CourseRoadmap(CourseBase):
    id: int
    is_enrolled: bool = False

    class Config:
        orm_mode = True


# Enrollment 관련 스키마
class EnrollmentBase(BaseModel):
    is_completed: bool = False


class EnrollmentCreate(EnrollmentBase):
    course_id: int


class Enrollment(EnrollmentBase):
    id: int
    user_id: int
    course_id: int

    class Config:
        orm_mode = True
