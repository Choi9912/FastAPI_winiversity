# app/api/v1/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta, datetime
from ...schemas import user as user_schema
from ...models.user import User, UserRole
from ...core import config
from ...core.security import verify_password, create_access_token, get_password_hash
from ...db.session import get_db

router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@router.post("/register", response_model=user_schema.User)
def register(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자입니다.")

    hashed_pw = get_password_hash(user.password)

    new_user = User(
        username=user.username,
        hashed_password=hashed_pw,
        nickname=user.nickname if user.nickname else None,
        role=user.role if user.role else UserRole.STUDENT,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/token", response_model=user_schema.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자 이름이나 비밀번호가 틀렸습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 로그인 시간 기록 추가
    user.last_login = datetime.utcnow()  # 현재 시간으로 설정
    db.commit()  # 변경 사항 커밋

    access_token_expires = timedelta(
        minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        subject=user.username, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(token: str = Depends(oauth2_scheme)):
    # 실제 로그아웃 로직은 클라이언트 측에서 처리해야 합니다.
    # 서버 측에서는 토큰을 블랙리스트에 추가하는 등의 추가 보안 조치를 취할 수 있습니다.
    return {"msg": "로그아웃 성공"}
