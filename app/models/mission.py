from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db.base import Base


class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    course = Column(String(20), index=True)
    question = Column(String, nullable=False)
    type = Column(String(20), nullable=False)  # "multiple_choice" or "code_submission"
    exam_type = Column(String(10), nullable=False)  # "midterm" or "final"

    multiple_choice = relationship(
        "MultipleChoiceMission", uselist=False, back_populates="mission"
    )
    code_submission = relationship(
        "CodeSubmissionMission", uselist=False, back_populates="mission"
    )
    submissions = relationship("MissionSubmission", back_populates="mission")


class MultipleChoiceMission(Base):
    __tablename__ = "multiple_choice_missions"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), unique=True)
    options = Column(JSON, nullable=False)  # List of options
    correct_answer = Column(String(1), nullable=False)  # 'A', 'B', 'C', 'D', 'E'

    mission = relationship("Mission", back_populates="multiple_choice")


class CodeSubmissionMission(Base):
    __tablename__ = "code_submission_missions"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), unique=True)
    problem_description = Column(String, nullable=False)
    initial_code = Column(String, nullable=True)
    test_cases = Column(JSON, nullable=False)  # List of test cases

    mission = relationship("Mission", back_populates="code_submission")


class MissionSubmission(Base):
    __tablename__ = "mission_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    mission_id = Column(Integer, ForeignKey("missions.id"))
    submitted_answer = Column(String, nullable=False)
    is_correct = Column(Boolean, default=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="missions_submissions")
    mission = relationship("Mission", back_populates="submissions")
    multiple_choice = relationship(
        "MultipleChoiceSubmission", uselist=False, back_populates="submission"
    )


class MultipleChoiceSubmission(Base):
    __tablename__ = "multiple_choice_submissions"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("mission_submissions.id"), unique=True)
    selected_option = Column(String(1), nullable=False)  # 'A', 'B', 'C', 'D', 'E'

    submission = relationship("MissionSubmission", back_populates="multiple_choice")
