from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class MultipleChoiceMissionBase(BaseModel):
    options: List[str]
    correct_answer: str = Field(..., pattern="^[A-E]$")

    model_config = ConfigDict(from_attributes=True)


class MultipleChoiceMissionCreate(MultipleChoiceMissionBase):
    pass


class MultipleChoiceMissionInDB(MultipleChoiceMissionBase):
    id: int
    mission_id: int


class CodeSubmissionMissionBase(BaseModel):
    problem_description: str
    initial_code: Optional[str] = None
    test_cases: List[dict]

    model_config = ConfigDict(from_attributes=True)


class CodeSubmissionMissionCreate(CodeSubmissionMissionBase):
    pass


class CodeSubmissionMissionInDB(CodeSubmissionMissionBase):
    id: int
    mission_id: int


class MissionBase(BaseModel):
    course: str
    question: str
    type: str
    exam_type: str

    model_config = ConfigDict(from_attributes=True)


class MissionCreate(MissionBase):
    multiple_choice: Optional[MultipleChoiceMissionCreate] = None
    code_submission: Optional[CodeSubmissionMissionCreate] = None


class MissionInDB(MissionBase):
    id: int
    multiple_choice: Optional[MultipleChoiceMissionInDB] = None
    code_submission: Optional[CodeSubmissionMissionInDB] = None


class MultipleChoiceSubmissionBase(BaseModel):
    selected_option: str = Field(..., pattern="^[A-E]$")

    model_config = ConfigDict(from_attributes=True)


class MultipleChoiceSubmissionCreate(MultipleChoiceSubmissionBase):
    pass


class MultipleChoiceSubmissionInDB(MultipleChoiceSubmissionBase):
    id: int
    submission_id: int


class MissionSubmissionBase(BaseModel):
    submitted_answer: str

    model_config = ConfigDict(from_attributes=True)


class MissionSubmissionCreate(MissionSubmissionBase):
    multiple_choice: Optional[MultipleChoiceSubmissionCreate] = None


class MissionSubmissionInDB(MissionSubmissionBase):
    id: int
    user_id: int
    mission_id: int
    is_correct: bool
    submitted_at: datetime
    multiple_choice: Optional[MultipleChoiceSubmissionInDB] = None
