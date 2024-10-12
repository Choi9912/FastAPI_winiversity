import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.courses import Course
from app.models.mission import Mission, MultipleChoiceMission, MissionSubmission
from tests.conftest import admin_authorized_client

@pytest.fixture
async def test_course(db_session: AsyncSession):
    course = Course(
        title=f"Test Course {uuid.uuid4().hex[:8]}",
        description="Test Description",
        price=100,
        is_paid=True,
        order=1  # order 필드 추가
    )
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)
    return course

@pytest.fixture
async def test_mission(db_session: AsyncSession, test_course: Course):
    async with db_session.begin():
        mission = Mission(
            course=str(test_course.id),  # course를 문자열로 변환
            question="Test question",
            type="multiple_choice",
            exam_type="QUIZ"
        )
        db_session.add(mission)
        await db_session.flush()

        multiple_choice = MultipleChoiceMission(
            mission_id=mission.id,
            options=["A", "B", "C", "D"],
            correct_answer="A"
        )
        db_session.add(multiple_choice)
    
    await db_session.refresh(mission)
    return mission

@pytest.mark.asyncio
async def test_get_missions(async_client: AsyncClient):
    response = await async_client.get("/api/v1/missions/")
    assert response.status_code == 200, f"Failed to get missions: {response.text}"
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_create_mission(admin_authorized_client: AsyncClient):
    mission_data = {
        "course": "TEST101",
        "question": "Test question",
        "type": "multiple_choice",
        "exam_type": "QUIZ",
        "multiple_choice": {
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A"
        }
    }
    
    response = await admin_authorized_client.post("/api/v1/missions/", json=mission_data)
    assert response.status_code in [200, 201], f"Failed to create mission: {response.text}"
    data = response.json()
    print(f"Server response: {data}")  # 서버 응답 전체를 출력

    assert "id" in data
    assert data["course"] == mission_data["course"]
    assert data["question"] == mission_data["question"]
    assert data["type"] == mission_data["type"]
    assert data["exam_type"] == mission_data["exam_type"]
    
    assert "multiple_choice" in data, "multiple_choice field is missing in the response"
    multiple_choice = data["multiple_choice"]
    assert multiple_choice is not None, "multiple_choice is None"
    assert "options" in multiple_choice, "options field is missing in multiple_choice"
    assert "correct_answer" in multiple_choice, "correct_answer field is missing in multiple_choice"
    
    options = multiple_choice["options"]
    assert isinstance(options, list), f"options is not a list, it's {type(options)}"
    assert set(options) == set(mission_data["multiple_choice"]["options"]), f"Options mismatch. Expected {mission_data['multiple_choice']['options']}, got {options}"
    
    assert multiple_choice["correct_answer"] == mission_data["multiple_choice"]["correct_answer"]

    print(f"Created mission: {data}")  # 생성된 미션 데이터 출력

@pytest.mark.asyncio
async def test_submit_mission(authorized_client: AsyncClient, test_mission: Mission, db_session: AsyncSession):
    submission_data = {
        "submitted_answer": "A",
        "multiple_choice": {
            "selected_option": "A"
        }
    }

    response = await authorized_client.post(f"/api/v1/missions/{test_mission.id}/submit", json=submission_data)
    assert response.status_code == 201, f"Failed to submit mission: {response.text}"
    data = response.json()
    assert "is_correct" in data
    assert data["is_correct"] == True

    # 데이터베이스에서 제출 기록을 확인합니다
    await db_session.refresh(test_mission)
    
    stmt = select(MissionSubmission).where(MissionSubmission.mission_id == test_mission.id)
    result = await db_session.execute(stmt)
    submission = result.scalar_one_or_none()
    
    assert submission is not None
    assert submission.is_correct == True
    assert submission.submitted_answer == "A"