from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...db.session import get_async_db
from ...models.user import User
from ...api.dependencies import get_current_active_user
from ...services.payment_service import PaymentService
from ...schemas import payment as payment_schema
from typing import List

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/prepare", response_model=payment_schema.PaymentPrepareResponse)
async def prepare_payment(
    payment: payment_schema.PaymentPrepareRequest,
    db: AsyncSession = Depends(get_async_db),
    payment_service: PaymentService = Depends()
):
    return await payment_service.prepare_payment(db, payment)

@router.post("/confirm", response_model=payment_schema.Payment)
async def confirm_payment(
    verification: payment_schema.PaymentConfirmRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    payment_service: PaymentService = Depends()
):
    return await payment_service.confirm_payment(db, current_user.id, verification)

@router.get("/history", response_model=List[payment_schema.Payment])
async def get_payment_history(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    payment_service: PaymentService = Depends()
):
    return await payment_service.get_payment_history(db, current_user.id)

@router.post("/refund/{payment_id}", response_model=payment_schema.Payment)
async def refund_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    payment_service: PaymentService = Depends()
):
    return await payment_service.refund_payment(db, current_user.id, payment_id)

@router.post("/apply_coupon", response_model=float)
async def apply_coupon(
    course_id: int,
    coupon_code: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    payment_service: PaymentService = Depends()
):
    return await payment_service.apply_coupon_to_course(db, course_id, coupon_code)