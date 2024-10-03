from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from ..models.payment import PaymentMethod, PaymentStatus
from enum import Enum


class PaymentCreate(BaseModel):
    course_id: int
    method: PaymentMethod

    model_config = {"from_attributes": True}


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

    model_config = {"from_attributes": True}


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
    coupon_code: Optional[str] = None  # 이 줄을 추가하세요


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
