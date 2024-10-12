import pytest
import asyncio
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base  
from app.db.session import get_async_db
from app.core.config import settings
from fastapi.testclient import TestClient
from app.core.security import get_password_hash
from app.models.user import User
from sqlalchemy.future import select
from app.core.config import settings
from app.models.courses import Course
TEST_SQLALCHEMY_DATABASE_URI = "sqlite+aiosqlite:///./test.db"

# SQLite 테스트 데이터베이스 URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="session")
def engine():
    return create_async_engine(TEST_SQLALCHEMY_DATABASE_URI, echo=True)

@pytest.fixture(scope="function")
async def db_session():
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="session")
async def init_test_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(autouse=True, scope="session")
async def initialize_db(init_test_db):
    # This fixture will run automatically before each session
    pass

@pytest.fixture(scope="function")
async def test_user(db_session: AsyncSession):
    unique_id = uuid.uuid4().hex[:8]
    password = "strongpassword"
    user_data = {
        "username": f"testuser_{unique_id}",
        "email": f"testuser_{unique_id}@example.com",
        "hashed_password": get_password_hash(password),
        "phone_number": "1234567890",
        "nickname": f"Test User {unique_id}",
        "role": "STUDENT"
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    print(f"Debug: Created test user with ID: {user.id}")
    
    # Verify the user was actually saved
    saved_user = await db_session.get(User, user.id)
    print(f"Debug: Retrieved saved user: {saved_user}")
    assert saved_user is not None, "Test user was not saved to the database"
    
    return user

@pytest.fixture(scope="function")
async def test_user_password():
    return "strongpassword"  # 비밀번호를 별도의 픽스처로 분리

@pytest.fixture(scope="function")
async def async_client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_async_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def admin_user(db_session: AsyncSession):
    unique_id = uuid.uuid4().hex[:8]
    user_data = {
        "username": f"adminuser_{unique_id}",
        "email": f"admin_{unique_id}@example.com",
        "password": "adminpassword",
        "phone_number": "9876543210",
        "nickname": f"Admin User {unique_id}",
        "role": "ADMIN"
    }

    hashed_password = get_password_hash(user_data["password"])
    db_user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=hashed_password,
        phone_number=user_data["phone_number"],
        nickname=user_data["nickname"],
        role=user_data["role"]
    )
    db_session.add(db_user)
    try:
        await db_session.commit()
        await db_session.refresh(db_user)
    except Exception as e:
        await db_session.rollback()
        pytest.fail(f"Failed to create admin user: {str(e)}")
    return db_user

@pytest.fixture(scope="function")
async def access_token(async_client, test_user, test_user_password):
    response = await async_client.post(
        "/api/v1/auth/token",
        data={"username": test_user.username, "password": test_user_password},
    )
    return response.json()["access_token"]

@pytest.fixture(scope="function")
async def authorized_client(async_client, access_token):
    async_client.headers.update({"Authorization": f"Bearer {access_token}"})
    return async_client

@pytest.fixture(scope="function")
async def admin_access_token(async_client, admin_user):
    response = await async_client.post(
        "/api/v1/auth/token",
        data={"username": admin_user.username, "password": "adminpassword"},
    )
    return response.json()["access_token"]

@pytest.fixture(scope="function")
async def admin_authorized_client(async_client, admin_access_token):
    async_client.headers.update({"Authorization": f"Bearer {admin_access_token}"})
    return async_client

@pytest.fixture
async def test_course(db_session: AsyncSession):
    course = Course(
        title=f"Test Course {uuid.uuid4().hex[:8]}",
        description="Test Description",
        price=100,
        is_paid=True,
        order=1
    )
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)
    return course

