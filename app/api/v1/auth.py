from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta, datetime
from ...schemas import user as user_schema
from ...models.user import User, UserRole
from ...core import config
from ...core.security import verify_password, create_access_token, get_password_hash, create_refresh_token, decode_token
from ...db.session import get_async_db
from sqlalchemy import select

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

@router.post("/register", response_model=user_schema.User)
async def register(
    user: user_schema.UserCreate, db: AsyncSession = Depends(get_async_db)
):
    """
    새로운 사용자를 등록합니다.
    - 중복된 사용자명 확인
    - 비밀번호 해싱
    - 새 사용자 생성 및 데이터베이스에 저장
    """
    print(f"Received user data: {user.model_dump()}")  
    result = await db.execute(select(User).where(User.username == user.username))
    db_user = result.scalar_one_or_none()
    if db_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자입니다.")

    hashed_pw = get_password_hash(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        phone_number=user.phone_number,
        hashed_password=hashed_pw,
        nickname=user.nickname,
        role=user.role,
        is_active=user.is_active,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/token", response_model=user_schema.TokenPair)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db),
):
    """
    사용자 로그인 및 액세스/리프레시 토큰 발급
    - 사용자 인증
    - 마지막 로그인 시간 업데이트
    - JWT 액세스 토큰 및 리프레시 토큰 생성 및 반환
    """
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자 이름이나 비밀번호가 틀렸습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user.last_login = datetime.utcnow()
    await db.commit()

    access_token_expires = timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=config.settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(
        subject=user.username, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        subject=user.username, expires_delta=refresh_token_expires
    )
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=user_schema.Token)
async def refresh_access_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_async_db),
):
    """
    리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급합니다.
    """
    try:
        payload = decode_token(refresh_token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    access_token_expires = timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.username, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(token: str = Depends(oauth2_scheme)):
    """
    사용자 로그아웃
    - 현재는 클라이언트 측에서 토큰을 삭제하는 것으로 처리
    """
    return {"msg": "로그아웃 성공"}
