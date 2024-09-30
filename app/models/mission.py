from sqlalchemy import Integer, String, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from ..db.base import Base
from typing import List, Optional


class Mission(Base):
    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    course: Mapped[str] = mapped_column(String(20), index=True)
    question: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    exam_type: Mapped[str] = mapped_column(String(10), nullable=False)

    multiple_choice: Mapped[Optional["MultipleChoiceMission"]] = relationship(
        "MultipleChoiceMission", uselist=False, back_populates="mission"
    )
    code_submission: Mapped[Optional["CodeSubmissionMission"]] = relationship(
        "CodeSubmissionMission", uselist=False, back_populates="mission"
    )
    submissions: Mapped[List["MissionSubmission"]] = relationship(
        "MissionSubmission", back_populates="mission"
    )


class MultipleChoiceMission(Base):
    __tablename__ = "multiple_choice_missions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    mission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("missions.id"), unique=True
    )
    options: Mapped[str] = mapped_column(JSON, nullable=False)
    correct_answer: Mapped[str] = mapped_column(String(1), nullable=False)

    mission: Mapped["Mission"] = relationship(
        "Mission", back_populates="multiple_choice"
    )


class CodeSubmissionMission(Base):
    __tablename__ = "code_submission_missions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    mission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("missions.id"), unique=True
    )
    problem_description: Mapped[str] = mapped_column(String, nullable=False)
    initial_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    test_cases: Mapped[str] = mapped_column(JSON, nullable=False)

    mission: Mapped["Mission"] = relationship(
        "Mission", back_populates="code_submission"
    )


class MissionSubmission(Base):
    __tablename__ = "mission_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    mission_id: Mapped[int] = mapped_column(Integer, ForeignKey("missions.id"))
    submitted_answer: Mapped[str] = mapped_column(String, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="missions_submissions")
    mission: Mapped["Mission"] = relationship("Mission", back_populates="submissions")
    multiple_choice: Mapped[Optional["MultipleChoiceSubmission"]] = relationship(
        "MultipleChoiceSubmission", uselist=False, back_populates="submission"
    )


class MultipleChoiceSubmission(Base):
    __tablename__ = "multiple_choice_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    submission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("mission_submissions.id"), unique=True
    )
    selected_option: Mapped[str] = mapped_column(String(1), nullable=False)

    submission: Mapped["MissionSubmission"] = relationship(
        "MissionSubmission", back_populates="multiple_choice"
    )
