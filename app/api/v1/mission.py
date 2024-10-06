from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ...schemas.mission import (
    MissionCreate,
    MissionInDB,
    MissionSubmissionCreate,
    MissionSubmissionInDB,
    MultipleChoiceMissionSchema,       # 추가
    CodeSubmissionMissionSchema        # 추가
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
from sqlalchemy.orm import relationship, joinedload, selectinload
from sqlalchemy.future import select

router = APIRouter(
    prefix="/missions",
    tags=["missions"],
)


@router.get("/", response_model=List[MissionInDB])
async def get_missions(db: AsyncSession = Depends(get_async_db)):
    async with db.begin():
        result = await db.execute(
            select(Mission).options(
                selectinload(Mission.multiple_choice),
                selectinload(Mission.code_submission)
            )
        )
        missions = result.scalars().all()

    return [
        MissionInDB(
            id=mission.id,
            course=mission.course,
            question=mission.question,
            type=mission.type,
            exam_type=mission.exam_type,
            multiple_choice=mission.multiple_choice.dict() if mission.multiple_choice else None,
            code_submission=mission.code_submission.dict() if mission.code_submission else None
        )
        for mission in missions
    ]


@router.get("/{mission_id}", response_model=MissionInDB)
async def retrieve_mission(mission_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(Mission)
        .options(joinedload(Mission.multiple_choice), joinedload(Mission.code_submission))
        .where(Mission.id == mission_id)
    )
    mission = result.unique().scalar_one_or_none()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    return MissionInDB(
        id=mission.id,
        course=mission.course,
        question=mission.question,
        type=mission.type,
        exam_type=mission.exam_type,
        multiple_choice=MultipleChoiceMissionSchema(
            options=mission.multiple_choice.options,
            correct_answer=mission.multiple_choice.correct_answer  # correct_answer_index에서 correct_answer로 변경
        ) if mission.multiple_choice else None,
        code_submission=CodeSubmissionMissionSchema(**mission.code_submission.__dict__) if mission.code_submission else None,
    )


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
    try:
        new_mission = Mission(
            course=mission.course,
            question=mission.question,
            type=mission.type,
            exam_type=mission.exam_type,
        )
        db.add(new_mission)
        await db.flush()

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
        
        # 명시적으로 관련 객체 로드
        result = await db.execute(
            select(Mission)
            .options(selectinload(Mission.multiple_choice), selectinload(Mission.code_submission))
            .where(Mission.id == new_mission.id)
        )
        loaded_mission = result.scalar_one()
        
        return MissionInDB(
            id=loaded_mission.id,
            course=loaded_mission.course,
            question=loaded_mission.question,
            type=loaded_mission.type,
            exam_type=loaded_mission.exam_type,
            multiple_choice={
                "options": loaded_mission.multiple_choice.options,
                "correct_answer": loaded_mission.multiple_choice.correct_answer
            } if loaded_mission.multiple_choice else None,
            code_submission={
                "problem_description": loaded_mission.code_submission.problem_description,
                "initial_code": loaded_mission.code_submission.initial_code,
                "test_cases": loaded_mission.code_submission.test_cases
            } if loaded_mission.code_submission else None
        )
    except Exception as e:
        await db.rollback()
        print(f"Error creating mission: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")