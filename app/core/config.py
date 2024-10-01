from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite+aiosqlite:///./database.db"
    IAMPORT_API_KEY: str = os.getenv("IAMPORT_API_KEY")
    IAMPORT_API_SECRET: str = os.getenv("IAMPORT_API_SECRET")

    class Config:
        env_file = ".env"


settings = Settings()
