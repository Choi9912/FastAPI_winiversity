from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any
from datetime import datetime


class MultipleChoiceMissionSchema(BaseModel):
    options: List[str]
    correct_answer: str = Field(..., pattern="^[A-E]$")

    model_config = {"from_attributes": True}


class CodeSubmissionMissionSchema(BaseModel):
    problem_description: str
    initial_code: Optional[str] = None
    test_cases: List[dict]

    model_config = {"from_attributes": True}


class MissionBase(BaseModel):
    course: str
    question: str
    type: str
    exam_type: str

    model_config = {"from_attributes": True}


class MissionCreate(BaseModel):
    course: str
    question: str
    type: str
    exam_type: str
    multiple_choice: Optional[MultipleChoiceMissionSchema] = None
    code_submission: Optional[CodeSubmissionMissionSchema] = None


class MissionInDB(MissionBase):
    id: int
    multiple_choice: Optional[MultipleChoiceMissionSchema] = None
    code_submission: Optional[CodeSubmissionMissionSchema] = None


class MultipleChoiceSubmissionSchema(BaseModel):
    selected_option: str = Field(..., pattern="^[A-E]$")

    model_config = {"from_attributes": True}


class MissionSubmissionBase(BaseModel):
    submitted_answer: str

    model_config = {"from_attributes": True}


class MissionSubmissionCreate(MissionSubmissionBase):
    multiple_choice: Optional[MultipleChoiceSubmissionSchema] = None


class MissionSubmissionInDB(MissionSubmissionBase):
    id: int
    user_id: int
    mission_id: int
    is_correct: bool
    submitted_at: datetime
    multiple_choice: Optional[MultipleChoiceSubmissionSchema] = None
