from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...schemas import user as user_schema
from ...models.user import User
from ...db.session import get_db
from ...api.dependencies import get_current_active_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


def require_admin(current_user: User = Depends(get_current_active_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="관리자 권한이 필요합니다."
        )
    return current_user


@router.get("/users", response_model=List[user_schema.User])
def get_all_users(
    db: Session = Depends(get_db), current_user: User = Depends(require_admin)
):
    users = db.query(User).all()
    return users


@router.get("/users/{user_id}", response_model=user_schema.User)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return user


# 추가적인 관리자 엔드포인트...
