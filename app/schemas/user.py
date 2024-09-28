from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class User(UserBase):
    id: int
    is_active: bool = True

    class Config:
        from_attributes = True


# Token 스키마 추가
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
