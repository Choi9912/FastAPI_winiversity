from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from ..db.base import Base
import enum


class UserRole(str, enum.Enum):
    STUDENT = "STUDENT"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    nickname = Column(String, nullable=True)
    total_learning_time = Column(Integer, default=0)  # 총 학습 시간 (분 단위)
    credits = Column(Integer, default=0)  # 학점
    course_valid_until = Column(DateTime, nullable=True)  # 수강 가능 기간

    enrollments = relationship("Enrollment", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    missions_submissions = relationship("MissionSubmission", back_populates="user")
    certificates = relationship("Certificate", back_populates="user")
    lesson_progress = relationship("LessonProgress", back_populates="user")
