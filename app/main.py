import asyncio
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.db.base import Base
from app.db.session import engine
from app.api.v1 import auth, users, admin, courses, payment, mission, certificates
from dotenv import load_dotenv
import logging
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행할 코드
    yield
    # 종료 시 실행할 코드

app = FastAPI(lifespan=lifespan)

# 정적 파일 설정


# 템플릿 설정
# templates = Jinja2Templates(directory="app/templates")


# 비동기 함수로 데이터베이스 테이블 생성
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# FastAPI 시작 이벤트에 테이블 생성 함수 추가
@app.on_event("startup")
async def startup_event():
    logger.info(f"Using database: {settings.DATABASE_URL}")
    await create_tables()


# 라우터 포함

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(courses.router, prefix="/api/v1")
app.include_router(payment.router, prefix="/api/v1")
app.include_router(mission.router, prefix="/api/v1")
app.include_router(certificates.router, prefix="/api/v1")





app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시에는 구체적인 origin을 지정하세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
