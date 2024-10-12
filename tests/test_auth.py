import pytest
from httpx import AsyncClient
from app.models.user import User

pytestmark = pytest.mark.asyncio

async def test_register_user(async_client):
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword",  
        "phone_number": "1234567890",
        "nickname": "New User",
        "role": "STUDENT"
    }
    response = await async_client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["username"] == user_data["username"]

@pytest.mark.asyncio
async def test_login_user(async_client: AsyncClient, test_user: User, test_user_password: str):
    login_data = {
        "username": test_user.username,
        "password": test_user_password
    }
    response = await async_client.post("/api/v1/auth/token", data=login_data)
    assert response.status_code == 200, f"Response: {response.text}"
    data = response.json()
    assert "access_token" in data

@pytest.mark.asyncio
async def test_logout_user(async_client: AsyncClient, test_user: User, test_user_password: str):
    login_data = {
        "username": test_user.username,
        "password": test_user_password
    }
    login_response = await async_client.post("/api/v1/auth/token", data=login_data)
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.post("/api/v1/auth/logout", headers=headers)
    assert response.status_code == 200, f"Logout failed: {response.text}"
    data = response.json()
    assert data["msg"] == "로그아웃 성공"