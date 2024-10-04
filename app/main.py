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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

app = FastAPI()

# 정적 파일 설정


# 템플릿 설정
templates = Jinja2Templates(directory="app/templates")


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
app.include_router(auth.router, tags=["authentication"])
app.include_router(users.router, tags=["users"])
app.include_router(admin.router, tags=["admin"])
app.include_router(courses.router, tags=["courses"])
app.include_router(payment.router, tags=["payments"])
app.include_router(mission.router, tags=["missions"])
app.include_router(certificates.router, tags=["certificates"])


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/payment")
async def payment_page(request: Request):
    return templates.TemplateResponse("payment.html", {"request": request})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
