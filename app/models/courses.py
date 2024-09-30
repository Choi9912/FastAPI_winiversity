from sqlalchemy import Column, Float, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from ..db.base import Base

# User 모델 임포트를 제거합니다. 대신 문자열로 관계를 정의합니다.


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    order = Column(Integer)
    is_paid = Column(Boolean, default=False)
    price = Column(Float, default=0.0)

    lessons = relationship("Lesson", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course")
    certificates = relationship("Certificate", back_populates="course")
    payments = relationship("Payment", back_populates="course")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    order = Column(Integer)
    video_url = Column(String)
    course_id = Column(Integer, ForeignKey("courses.id"))

    course = relationship("Course", back_populates="lessons")
    steps = relationship("LessonStep", back_populates="lesson")
    progress = relationship("LessonProgress", back_populates="lesson")


class LessonStep(Base):
    __tablename__ = "lesson_steps"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    order = Column(Integer)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))

    lesson = relationship("Lesson", back_populates="steps")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    is_completed = Column(Boolean, default=False)

    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class LessonProgress(Base):
    __tablename__ = "lesson_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    last_watched_position = Column(Float, default=0)
    is_completed = Column(Boolean, default=False)

    user = relationship("User", back_populates="lesson_progress")
    lesson = relationship("Lesson", back_populates="progress")


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    issue_date = Column(DateTime)
    certificate_number = Column(String, unique=True, index=True)

    user = relationship("User", back_populates="certificates")
    course = relationship("Course", back_populates="certificates")


# User 모델과 Course 모델에 대한 관계 정의를 제거합니다.
# 대신 User 모델에서 이러한 관계를 정의해야 합니다.
