from fastapi import FastAPI
from .db.base import Base
from .db.session import engine
from .api.v1 import auth, users, admin, courses, payment, mission, certificates

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 라우터 포함
app.include_router(auth.router, tags=["authentication"])
app.include_router(users.router, tags=["users"])
app.include_router(admin.router, tags=["admin"])
app.include_router(courses.router, tags=["courses"])
app.include_router(payment.router, tags=["payment"])
app.include_router(mission.router, tags=["missions"])
app.include_router(certificates.router, tags=["certificates"])
