from pydantic import BaseModel
from typing import List, Optional


class LessonStepBase(BaseModel):
    title: str
    content: str
    order: int

    model_config = {"from_attributes": True}


class LessonStepCreate(LessonStepBase):
    pass


class LessonStepInDB(LessonStepBase):
    id: int
    lesson_id: int


class LessonBase(BaseModel):
    title: str
    content: str
    order: int
    video_url: str

    model_config = {"from_attributes": True}


class LessonCreate(LessonBase):
    steps: List[LessonStepCreate]


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    order: Optional[int] = None
    steps: Optional[List[LessonStepCreate]] = None

    model_config = {"from_attributes": True}


class LessonInDB(LessonBase):
    id: int
    course_id: int
    steps: List[LessonStepInDB]


class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    order: int
    is_paid: bool = False
    price: float = 0.0

    model_config = {"from_attributes": True}


class CourseCreate(CourseBase):
    lessons: List[LessonCreate]


class CourseInDB(CourseBase):
    id: int
    lessons: List[LessonInDB]  # Optional[List[LessonInDB]]가 아닌지 확인

    class Config:
        orm_mode = True  # Pydantic v1.x 사용 시
        # Pydantic v2.x 사용 시 다음과 같이 설정
        model_config = {
            "from_attributes": True,
        }


class CourseRoadmap(CourseBase):
    id: int
    is_enrolled: bool = False

    model_config = {"from_attributes": True}


class EnrollmentBase(BaseModel):
    is_completed: bool = False

    model_config = {"from_attributes": True}


class EnrollmentCreate(EnrollmentBase):
    course_id: int


class Enrollment(EnrollmentBase):
    id: int
    user_id: int
    course_id: int

    model_config = {"from_attributes": True}


class LessonProgressBase(BaseModel):
    last_watched_position: float
    is_completed: bool = False

    model_config = {"from_attributes": True}


class LessonProgressCreate(LessonProgressBase):
    lesson_id: int


class LessonProgressUpdate(LessonProgressBase):
    pass


class LessonProgressInDB(LessonProgressBase):
    id: int
    user_id: int
    lesson_id: int

    model_config = {"from_attributes": True}
