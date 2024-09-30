from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...schemas.mission import (
    MissionCreate,
    MissionInDB,
    MissionSubmissionCreate,
    MissionSubmissionInDB,
)
from ...models.mission import (
    Mission,
    MultipleChoiceMission,
    CodeSubmissionMission,
    MissionSubmission,
    MultipleChoiceSubmission,
)
from ...db.session import get_db
from ...api.dependencies import (
    get_current_active_user,
    get_current_user,
    get_current_admin_user,
)
import sys
from io import StringIO
from ...models.user import User

router = APIRouter(
    prefix="/missions",
    tags=["missions"],
)


@router.get("/", response_model=List[MissionInDB])
def list_missions(db: Session = Depends(get_db)):
    missions = db.query(Mission).all()
    return missions


@router.get("/{mission_id}", response_model=MissionInDB)
def retrieve_mission(mission_id: int, db: Session = Depends(get_db)):
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission


@router.post(
    "/{mission_id}/submit",
    response_model=MissionSubmissionInDB,
    status_code=status.HTTP_201_CREATED,
)
def submit_mission(
    mission_id: int,
    submission: MissionSubmissionCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    if mission.type == "multiple_choice":
        selected_option = (
            submission.multiple_choice.selected_option
            if submission.multiple_choice
            else None
        )
        if not selected_option:
            raise HTTPException(status_code=400, detail="Selected option is required")

        correct_option = mission.multiple_choice.correct_answer
        is_correct = selected_option == correct_option

        mission_submission = MissionSubmission(
            user_id=current_user,
            mission_id=mission.id,
            submitted_answer=selected_option,
            is_correct=is_correct,
        )
        db.add(mission_submission)
        db.commit()
        db.refresh(mission_submission)
        return mission_submission

    elif mission.type == "code_submission":
        submitted_code = submission.submitted_answer
        if not submitted_code:
            raise HTTPException(status_code=400, detail="No code submitted.")

        is_correct, output = execute_and_grade_code(
            mission.code_submission, submitted_code
        )

        mission_submission = MissionSubmission(
            user_id=current_user,
            mission_id=mission.id,
            submitted_answer=submitted_code,
            is_correct=is_correct,
        )
        db.add(mission_submission)
        db.commit()
        db.refresh(mission_submission)
        return mission_submission

    else:
        raise HTTPException(status_code=400, detail="Invalid mission type")


def execute_and_grade_code(code_mission: CodeSubmissionMission, submitted_code: str):
    original_stdout = sys.stdout
    redirected_output = StringIO()
    sys.stdout = redirected_output

    outputs = []
    all_correct = True

    try:
        exec(submitted_code, globals())

        for test_case in code_mission.test_cases:
            input_data = test_case["input"]
            expected_output = test_case["output"]

            try:
                actual_output = solution(input_data)

                if actual_output == expected_output:
                    outputs.append(
                        f"Test case passed: Input: {input_data}, Output: {actual_output}"
                    )
                else:
                    all_correct = False
                    outputs.append(
                        f"Test case failed: Input: {input_data}, Expected: {expected_output}, Got: {actual_output}"
                    )
            except Exception as e:
                all_correct = False
                outputs.append(
                    f"Error in test case: Input: {input_data}, Error: {str(e)}"
                )

    except Exception as e:
        all_correct = False
        outputs.append(f"Error occurred: {str(e)}")

    finally:
        sys.stdout = original_stdout

    return all_correct, "\n".join(outputs)


@router.post("/", response_model=MissionInDB)
def create_mission(
    mission: MissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    new_mission = Mission(
        course=mission.course,
        question=mission.question,
        type=mission.type,
        exam_type=mission.exam_type,
    )
    db.add(new_mission)
    db.flush()  # to get the new mission's id

    if mission.type == "multiple_choice" and mission.multiple_choice:
        multiple_choice = MultipleChoiceMission(
            mission_id=new_mission.id,
            options=mission.multiple_choice.options,
            correct_answer=mission.multiple_choice.correct_answer,
        )
        db.add(multiple_choice)
    elif mission.type == "code_submission" and mission.code_submission:
        code_submission = CodeSubmissionMission(
            mission_id=new_mission.id,
            problem_description=mission.code_submission.problem_description,
            initial_code=mission.code_submission.initial_code,
            test_cases=mission.code_submission.test_cases,
        )
        db.add(code_submission)

    db.commit()
    db.refresh(new_mission)
    return new_mission
