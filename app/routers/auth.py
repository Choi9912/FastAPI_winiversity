from fastapi import APIRouter

from app.schemas.user import UserCreate

router = APIRouter()


@router.post("/register")
async def register_user(user: UserCreate):
    # 사용자 등록 로직
    ...
