from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from ..models.user import UserRole


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=50)
    is_active: Optional[bool] = True
    role: Optional[UserRole] = UserRole.STUDENT  # 기본값을 STUDENT로 설정
    nickname: Optional[str] = Field(None, max_length=50)

    class Config:
        schema_extra = {"example": {"username": "vkvkd9", "password": "qwer1234"}}


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    credits: Optional[int] = None
    total_learning_time: Optional[int] = None
    course_valid_until: Optional[datetime] = None


class User(UserBase):
    id: int
    is_active: bool = True
    role: UserRole
    nickname: Optional[str] = None
    credits: int
    total_learning_time: int
    course_valid_until: Optional[datetime] = None

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# 이 부분을 추가합니다
user_schema = {
    "UserBase": UserBase,
    "UserCreate": UserCreate,
    "UserUpdate": UserUpdate,
    "User": User,
    "Token": Token,
    "TokenData": TokenData,
}
