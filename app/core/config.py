from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://postgres:1234@localhost/dbname"
    )

    # PortOne 관련 설정 추가
    portone_store_id: str
    portone_channel_group_id: str
    portone_api_url: str

    # 인증서 파일이 저장될 디렉토리
    CERTIFICATE_DIR: str = os.getenv(
        "CERTIFICATE_DIR", "/path/to/certificate/directory"
    )

    class Config:
        env_file = ".env"
        extra = "ignore"  # 추가 필드 무시


settings = Settings()
