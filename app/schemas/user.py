from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional
from ..models.user import UserRole
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str
    phone_number: str 

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    username: str
    email: EmailStr  
    password: str
    nickname: str
    role: UserRole = UserRole.STUDENT
    is_active: bool = True
    phone_number: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "vkvkd9",
                "email": "user@example.com",
                "password": "qwer1234",
                "nickname": "Nick",
                "phone_number": "1234567890",
                "is_active": True,
                "role": "STUDENT",
            }
        }
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


class Certificate(BaseModel):
    id: int
    course_id: int
    issue_date: datetime
    certificate_number: str

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None

    model_config = {"from_attributes": True}


class TokenPair(Token):
    refresh_token: str


user_schema = {
    "UserBase": UserBase,
    "UserCreate": UserCreate,
    "UserUpdate": UserUpdate,
    "User": User,
    "Token": Token,
    "TokenData": TokenData,
}
