import pytest
from httpx import AsyncClient
import logging
from app.models.user import User

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
@pytest.mark.asyncio
async def test_get_all_users(async_client: AsyncClient, admin_user: User):
    login_data = {
        "username": admin_user.username,
        "password": "adminpassword"
    }
    login_response = await async_client.post("/api/v1/auth/token", data=login_data)
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.get("/api/v1/admin/users", headers=headers)
    assert response.status_code == 200, f"Failed to get users: {response.text}"
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_get_user_by_id(async_client: AsyncClient, admin_user: User, test_user: User):
    # Login as admin
    login_data = {
        "username": admin_user.username,
        "password": "adminpassword"
    }
    login_response = await async_client.post("/api/v1/auth/token", data=login_data)
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get user by ID
    user_id = test_user.id
    response = await async_client.get(f"/api/v1/admin/users/{user_id}", headers=headers)
    assert response.status_code == 200, f"Failed to get user: {response.text}"
    user = response.json()
    assert user["id"] == user_id