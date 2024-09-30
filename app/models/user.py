from sqlalchemy import Boolean, Integer, String, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base import Base
import enum
from typing import List, Optional
from datetime import datetime


class UserRole(str, enum.Enum):
    STUDENT = "STUDENT"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.STUDENT)
    nickname: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    total_learning_time: Mapped[int] = mapped_column(Integer, default=0)
    credits: Mapped[int] = mapped_column(Integer, default=0)
    course_valid_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    enrollments: Mapped[List["Enrollment"]] = relationship(
        "Enrollment", back_populates="user"
    )
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="user")
    missions_submissions: Mapped[List["MissionSubmission"]] = relationship(
        "MissionSubmission", back_populates="user"
    )
    certificates: Mapped[List["Certificate"]] = relationship(
        "Certificate", back_populates="user"
    )
    lesson_progress: Mapped[List["LessonProgress"]] = relationship(
        "LessonProgress", back_populates="user"
    )
