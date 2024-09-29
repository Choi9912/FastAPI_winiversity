from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...schemas import user as user_schema
from ...models.user import User, UserRole
from ...core import security
from ...db.session import get_db
from ...api.dependencies import get_current_active_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_active_user)],
)


@router.get("/me", response_model=user_schema.User)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=user_schema.User)
def update_user_profile(
    user_update: user_schema.UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "student":  # 역할 검사 추가
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    user_data = user_update.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(current_user, key, value)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != "student":  # 역할 검사 추가
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    db.delete(current_user)
    db.commit()
    return


@router.post("/", response_model=user_schema.User)
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = security.get_password_hash(user.password)
    db_user = User(
        username=user.username,
        hashed_password=hashed_password,
        is_active=user.is_active,
        role=user.role,
        nickname=user.nickname,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
