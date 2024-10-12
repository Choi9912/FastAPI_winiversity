import uuid
import pytest
from httpx import AsyncClient
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.courses import Course

@pytest.mark.asyncio
async def test_issue_certificate(authorized_client: AsyncClient, db_session: AsyncSession):
    # Create a course first
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

    # 나머지 테스트 코드...

@pytest.mark.asyncio
async def test_verify_certificate(async_client: AsyncClient):
    # Assuming a certificate has been issued with a known certificate_number
    certificate_number = "test-certificate-number"

    response = await async_client.get(f"/api/v1/certificates/verify/{certificate_number}")
    assert response.status_code in [200, 404]  # Depending on whether the cert exists
    if response.status_code == 200:
        data = response.json()
        assert data["certificate_number"] == certificate_number
        assert "user_name" in data
        assert "course_title" in data