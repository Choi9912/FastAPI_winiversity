from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models import User
from app.schemas import UserOut

router = APIRouter()


@router.get("/", response_model=dict)
async def admin_root():
    return {"message": "Welcome to the admin panel"}


@router.get("/users", response_model=list[UserOut])
async def get_users(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
    users = db.query(User).all()
    return users


# 필요한 다른 관리자 엔드포인트들을 여기에 추가...
