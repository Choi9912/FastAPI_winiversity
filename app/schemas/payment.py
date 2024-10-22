from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from ..models.payment import PaymentMethod
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PaymentBase(BaseModel):
    amount: float
    method: str
    status: PaymentStatus


class PaymentCreate(PaymentBase):
    user_id: int
    course_id: int


class Payment(PaymentBase):
    id: int
    user_id: int
    course_id: int
    created_at: datetime
    completed_at: datetime | None
    expiration_date: datetime | None

    class Config:
        from_attributes = True


class CouponCreate(BaseModel):
    code: str
    discount_percent: float
    valid_until: datetime

    model_config = {"from_attributes": True}


class CouponResponse(BaseModel):
    id: int
    code: str
    discount_percent: float
    valid_until: datetime

    model_config = {"from_attributes": True}


class PaymentPrepareRequest(BaseModel):
    course_id: int
    method: str
    coupon_code: Optional[str] = None  


class CustomerInfo(BaseModel):
    customerId: str
    fullName: str
    phoneNumber: str
    email: str


class PaymentPrepareResponse(BaseModel):
    storeId: str
    channelGroupId: str
    paymentId: str
    orderName: str
    totalAmount: float
    currency: str
    payMethod: str
    customer: CustomerInfo


class PaymentConfirmRequest(BaseModel):
    imp_uid: str
    merchant_uid: str
