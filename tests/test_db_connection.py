import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

pytestmark = pytest.mark.asyncio

async def test_db_connection(db_session: AsyncSession):
    try:
        result = await db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1
        print("Database connection successful")
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")