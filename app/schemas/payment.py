from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from ..models.payment import PaymentMethod, PaymentStatus  # 수정된 부분


class PaymentCreate(BaseModel):
    course_id: int
    method: PaymentMethod


class PaymentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    amount: float
    method: PaymentMethod
    status: PaymentStatus
    created_at: datetime
    completed_at: Optional[datetime]
    expiration_date: datetime

    class Config:
        orm_mode = True


class CouponCreate(BaseModel):
    code: str
    discount_percent: float
    valid_until: datetime


class CouponResponse(BaseModel):
    id: int
    code: str
    discount_percent: float
    valid_until: datetime

    class Config:
        orm_mode = True
