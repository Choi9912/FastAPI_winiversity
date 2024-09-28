from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from ...schemas import user as user_schema
from ...models import user as user_model
from ...core import config
from ...core.security import verify_password, create_access_token, get_password_hash
from ...db.session import get_db

router = APIRouter()


@router.post("/register", response_model=user_schema.User)
def register(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = (
        db.query(user_model.User)
        .filter(user_model.User.username == user.username)
        .first()
    )
    if db_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자입니다.")
    hashed_pw = get_password_hash(user.password)  # 이 부분을 수정했습니다
    new_user = user_model.User(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/token", response_model=user_schema.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = (
        db.query(user_model.User)
        .filter(user_model.User.username == form_data.username)
        .first()
    )
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자 이름이나 비밀번호가 틀렸습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        subject=user.username, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
