from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional
from ..models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    username: str
    phone_number: str  # 새로 추가된 필드

    model_config = {"from_attributes": True}


class UserCreate(UserBase):
    password: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "username": "vkvkd9",
                "password": "qwer1234",
                "is_active": True,
                "role": "STUDENT",
                "nickname": "Nick",
            }
        },
    }


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    credits: Optional[int] = None
    total_learning_time: Optional[int] = None
    course_valid_until: Optional[datetime] = None
    phone_number: Optional[str] = None
    model_config = {"from_attributes": True}


class User(UserBase):
    id: int
    is_active: bool = True
    role: UserRole
    nickname: Optional[str] = None
    credits: int
    total_learning_time: int
    course_valid_until: Optional[datetime] = None

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str

    model_config = {"from_attributes": True}


class TokenData(BaseModel):
    username: Optional[str] = None

    model_config = {"from_attributes": True}


user_schema = {
    "UserBase": UserBase,
    "UserCreate": UserCreate,
    "UserUpdate": UserUpdate,
    "User": User,
    "Token": Token,
    "TokenData": TokenData,
}
