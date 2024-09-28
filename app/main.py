from fastapi import FastAPI
from .db.base import Base
from .db.session import engine
from .api.v1 import auth

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
