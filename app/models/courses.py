from sqlalchemy import Float, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base import Base
from typing import List, Optional
from datetime import datetime


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String)
    order: Mapped[int] = mapped_column(Integer)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    price: Mapped[float] = mapped_column(Float, default=0.0)

    lessons: Mapped[List["Lesson"]] = relationship("Lesson", back_populates="course")
    enrollments: Mapped[List["Enrollment"]] = relationship(
        "Enrollment", back_populates="course"
    )
    certificates: Mapped[List["Certificate"]] = relationship(
        "Certificate", back_populates="course"
    )
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="course")


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    content: Mapped[str] = mapped_column(String)
    order: Mapped[int] = mapped_column(Integer)
    video_url: Mapped[str] = mapped_column(String)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"))

    course: Mapped["Course"] = relationship("Course", back_populates="lessons")
    steps: Mapped[List["LessonStep"]] = relationship(
        "LessonStep", back_populates="lesson"
    )
    progress: Mapped[List["LessonProgress"]] = relationship(
        "LessonProgress", back_populates="lesson"
    )


class LessonStep(Base):
    __tablename__ = "lesson_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    content: Mapped[str] = mapped_column(String)
    order: Mapped[int] = mapped_column(Integer)
    lesson_id: Mapped[int] = mapped_column(Integer, ForeignKey("lessons.id"))

    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="steps")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"))
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship("User", back_populates="enrollments")
    course: Mapped["Course"] = relationship("Course", back_populates="enrollments")


class LessonProgress(Base):
    __tablename__ = "lesson_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    lesson_id: Mapped[int] = mapped_column(Integer, ForeignKey("lessons.id"))
    last_watched_position: Mapped[float] = mapped_column(Float, default=0)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship("User", back_populates="lesson_progress")
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="progress")


class Certificate(Base):
    __tablename__ = "certificates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"))
    issue_date: Mapped[datetime] = mapped_column(DateTime)
    certificate_number: Mapped[str] = mapped_column(String, unique=True, index=True)

    user: Mapped["User"] = relationship("User", back_populates="certificates")
    course: Mapped["Course"] = relationship("Course", back_populates="certificates")