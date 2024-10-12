import pytest
from httpx import AsyncClient
from app.schemas import user as user_schema

@pytest.mark.asyncio
async def test_read_users_me(async_client: AsyncClient, test_user, test_user_password):
    login_data = {
        "username": test_user.username,
        "password": test_user_password
    }
    login_response = await async_client.post("/api/v1/auth/token", data=login_data)
    assert login_response.status_code == 200, f"Login failed: {login_response.content}"
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200, f"Failed to get user: {response.content}"
    data = response.json()
    assert data["username"] == test_user.username

@pytest.mark.asyncio
async def test_update_user_profile(async_client, test_user, access_token):
    user_id = test_user.id
    print(f"Debug: test_user.id = {user_id}")
    print(f"Debug: test_user.__dict__ = {test_user.__dict__}")

    # Verify user exists
    response = await async_client.get(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"Debug: Get user response: {response.status_code}, {response.content}")
    assert response.status_code == 200, f"User not found. Response: {response.content}"
    
    update_data = {
        "nickname": "Updated Nickname",
        "phone_number": "9876543210"
    }
    
    # Debug: Print user_id and access_token
    print(f"Debug: user_id = {user_id}")
    print(f"Debug: access_token = {access_token}")
    
    response = await async_client.put(
        f"/api/v1/users/{user_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    # Debug: Print response status and content
    print(f"Debug: Response status = {response.status_code}")
    print(f"Debug: Response content = {response.content}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.content}"
    # ... rest of the test ...

@pytest.mark.asyncio
async def test_delete_user_account(async_client: AsyncClient):
    # Register a new user to delete
    register_data = {
        "username": "deleteuser",
        "email": "deleteuser@example.com",
        "phone_number": "01087654321",
        "password": "deletepassword",
        "nickname": "DeleteUser",
        "role": "STUDENT",
        "is_active": True
    }
    await async_client.post("api/v1/auth/register", json=register_data)

    # Login to get the token
    login_data = {
        "username": "deleteuser",
        "password": "deletepassword"
    }
    login_response = await async_client.post("api/v1/auth/token", data=login_data)
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.delete("api/v1/users/me", headers=headers)
    assert response.status_code == 204

    # Verify deletion
    get_response = await async_client.get("api/v1/users/me", headers=headers)
    assert get_response.status_code == 401  # Unauthorized, as the user no longer exists

    # Try to login again to confirm the user is deleted
    login_response = await async_client.post("api/v1/auth/token", data=login_data)
    assert login_response.status_code == 401  # Unauthorized, as the user no longer exists