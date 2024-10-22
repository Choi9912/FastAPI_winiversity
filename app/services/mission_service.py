from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..models.mission import Mission, MultipleChoiceMission, CodeSubmissionMission, MissionSubmission
from ..schemas import mission as mission_schema
from fastapi import HTTPException
from typing import List, Tuple
import sys
from io import StringIO

class MissionService:
    async def get_missions(self, db: AsyncSession) -> List[Mission]:
        result = await db.execute(
            select(Mission).options(
                selectinload(Mission.multiple_choice),
                selectinload(Mission.code_submission)
            )
        )
        return result.scalars().all()

    async def retrieve_mission(self, db: AsyncSession, mission_id: int) -> Mission:
        result = await db.execute(
            select(Mission)
            .options(selectinload(Mission.multiple_choice), selectinload(Mission.code_submission))
            .where(Mission.id == mission_id)
        )
        mission = result.unique().scalar_one_or_none()
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")
        return mission

    async def submit_mission(self, db: AsyncSession, mission_id: int, user_id: int, submission: mission_schema.MissionSubmissionCreate) -> MissionSubmission:
        mission = await self.retrieve_mission(db, mission_id)

        if mission.type == "multiple_choice":
            return await self._submit_multiple_choice(db, mission, user_id, submission)
        elif mission.type == "code_submission":
            return await self._submit_code(db, mission, user_id, submission)
        else:
            raise HTTPException(status_code=400, detail="Invalid mission type")

    async def _submit_multiple_choice(self, db: AsyncSession, mission: Mission, user_id: int, submission: mission_schema.MissionSubmissionCreate) -> MissionSubmission:
        selected_option = submission.multiple_choice.selected_option if submission.multiple_choice else None
        if not selected_option:
            raise HTTPException(status_code=400, detail="Selected option is required")

        correct_option = mission.multiple_choice.correct_answer
        is_correct = selected_option == correct_option

        mission_submission = MissionSubmission(
            user_id=user_id,
            mission_id=mission.id,
            submitted_answer=selected_option,
            is_correct=is_correct,
        )
        db.add(mission_submission)
        await db.commit()
        await db.refresh(mission_submission)
        return mission_submission

    async def _submit_code(self, db: AsyncSession, mission: Mission, user_id: int, submission: mission_schema.MissionSubmissionCreate) -> MissionSubmission:
        submitted_code = submission.submitted_answer
        if not submitted_code:
            raise HTTPException(status_code=400, detail="No code submitted.")

        is_correct, output = self._execute_and_grade_code(mission.code_submission, submitted_code)

        mission_submission = MissionSubmission(
            user_id=user_id,
            mission_id=mission.id,
            submitted_answer=submitted_code,
            is_correct=is_correct,
        )
        db.add(mission_submission)
        await db.commit()
        await db.refresh(mission_submission)
        return mission_submission

    def _execute_and_grade_code(self, code_mission: CodeSubmissionMission, submitted_code: str) -> Tuple[bool, str]:
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()

        is_correct = True
        output = ""

        try:
            exec(submitted_code)

            for test_case in code_mission.test_cases:
                sys.stdin = StringIO(test_case["input"])

                exec(submitted_code)

                result = redirected_output.getvalue().strip()
                if result != test_case["expected_output"].strip():
                    is_correct = False
                    output += f"Test case failed. Input: {test_case['input']}, Expected: {test_case['expected_output']}, Got: {result}\n"

                redirected_output.truncate(0)
                redirected_output.seek(0)

        except Exception as e:
            is_correct = False
            output = f"Error occurred: {str(e)}"

        finally:
            sys.stdout = old_stdout
            sys.stdin = sys.__stdin__

        return is_correct, output

    async def create_mission(self, db: AsyncSession, mission: mission_schema.MissionCreate) -> Mission:
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
        
        result = await db.execute(
            select(Mission)
            .options(selectinload(Mission.multiple_choice), selectinload(Mission.code_submission))
            .where(Mission.id == new_mission.id)
        )
        return result.scalar_one()