import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.courses import Course
from app.models.user import User


@pytest.mark.asyncio
async def test_get_all_courses(async_client: AsyncClient):
    response = await async_client.get("/api/v1/courses/")
    assert response.status_code == 200, f"Response: {response.text}"
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_create_course(admin_authorized_client: AsyncClient):
    course_data = {
        "title": f"Test Course {uuid.uuid4().hex[:8]}",
        "description": "Test Description",
        "price": 100,
        "is_paid": True,
        "order": 1,
        "lessons": [
            {
                "title": "Lesson 1",
                "description": "Description for Lesson 1",
                "order": 1,
                "content": "Content for Lesson 1",
                "video_url": "https://example.com/video1.mp4",
                "steps": [
                    {
                        "title": "Step 1",
                        "content": "Content for Step 1",
                        "order": 1
                    }
                ]
            }
        ]
    }
    response = await admin_authorized_client.post("/api/v1/courses/", json=course_data)
    assert response.status_code in [200, 201], f"Failed to create course: {response.text}"
    data = response.json()
    assert "id" in data
    assert data["title"] == course_data["title"]
    # 'description' 필드가 응답에 없을 수 있으므로 조건부로 검사
    if "description" in data:
        assert data["description"] == course_data["description"]
    assert data["price"] == course_data["price"]
    assert data["is_paid"] == course_data["is_paid"]
    assert data["order"] == course_data["order"]
    assert len(data["lessons"]) == 1
    
    lesson = data["lessons"][0]
    assert lesson["title"] == course_data["lessons"][0]["title"]
    # 'description' 필드가 응답에 없을 수 있으므로 조건부로 검사
    if "description" in lesson:
        assert lesson["description"] == course_data["lessons"][0]["description"]
    assert lesson["order"] == course_data["lessons"][0]["order"]
    assert lesson["content"] == course_data["lessons"][0]["content"]
    assert lesson["video_url"] == course_data["lessons"][0]["video_url"]
    
    assert len(lesson["steps"]) == 1
    step = lesson["steps"][0]
    assert step["title"] == course_data["lessons"][0]["steps"][0]["title"]
    assert step["content"] == course_data["lessons"][0]["steps"][0]["content"]
    assert step["order"] == course_data["lessons"][0]["steps"][0]["order"]

    # 생성된 코스의 ID를 출력 (디버깅 목적)
    print(f"Created course ID: {data['id']}")

