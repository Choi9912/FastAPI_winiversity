from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
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
from ...db.session import get_async_db
from ...api.dependencies import (
    get_current_active_user,
    get_current_user,
    get_current_admin_user,
)
import sys
from io import StringIO
from ...models.user import User
from sqlalchemy import select

router = APIRouter(
    prefix="/missions",
    tags=["missions"],
)


@router.get("/", response_model=List[MissionInDB])
async def list_missions(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Mission))
    missions = result.scalars().all()
    return missions


@router.get("/{mission_id}", response_model=MissionInDB)
async def retrieve_mission(mission_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Mission).where(Mission.id == mission_id))
    mission = result.scalar_one_or_none()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission


@router.post(
    "/{mission_id}/submit",
    response_model=MissionSubmissionInDB,
    status_code=status.HTTP_201_CREATED,
)
async def submit_mission(
    mission_id: int,
    submission: MissionSubmissionCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: int = Depends(get_current_user),
):
    result = await db.execute(select(Mission).where(Mission.id == mission_id))
    mission = result.scalar_one_or_none()
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
        await db.commit()
        await db.refresh(mission_submission)
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
        await db.commit()
        await db.refresh(mission_submission)
        return mission_submission

    else:
        raise HTTPException(status_code=400, detail="Invalid mission type")


def execute_and_grade_code(code_mission: CodeSubmissionMission, submitted_code: str):
    # 제출된 코드의 출력을 캡처하기 위한 설정
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()

    is_correct = True
    output = ""

    try:
        # 제출된 코드 실행
        exec(submitted_code)

        # 테스트 케이스 실행
        for test_case in code_mission.test_cases:
            # 테스트 케이스 입력 설정
            sys.stdin = StringIO(test_case["input"])

            # 테스트 케이스 실행
            exec(submitted_code)

            # 출력 확인
            result = redirected_output.getvalue().strip()
            if result != test_case["expected_output"].strip():
                is_correct = False
                output += f"Test case failed. Input: {test_case['input']}, Expected: {test_case['expected_output']}, Got: {result}\n"

            # 출력 버퍼 초기화
            redirected_output.truncate(0)
            redirected_output.seek(0)

    except Exception as e:
        is_correct = False
        output = f"Error occurred: {str(e)}"

    finally:
        # 표준 출력 및 입력 복원
        sys.stdout = old_stdout
        sys.stdin = sys.__stdin__

    return is_correct, output


@router.post("/", response_model=MissionInDB)
async def create_mission(
    mission: MissionCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    new_mission = Mission(
        course=mission.course,
        question=mission.question,
        type=mission.type,
        exam_type=mission.exam_type,
    )
    db.add(new_mission)
    await db.flush()  # to get the new mission's id

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

    await db.commit()
    await db.refresh(new_mission)
    return new_mission
