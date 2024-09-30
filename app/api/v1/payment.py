from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...db.session import get_async_db
from ...models.user import User
from ...models.courses import Course
from ...models.payment import Payment, PaymentStatus, Coupon
from ...schemas import payment as payment_schema
from ..dependencies import get_current_active_user
from datetime import datetime, timedelta
from typing import List
from sqlalchemy import select

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)


@router.post("/", response_model=payment_schema.PaymentResponse)
async def create_payment(
    payment: payment_schema.PaymentCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    course_result = await db.execute(
        select(Course).where(Course.id == payment.course_id)
    )
    course = course_result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user already paid for this course
    existing_payment_result = await db.execute(
        select(Payment).where(
            Payment.user_id == current_user.id,
            Payment.course_id == course.id,
            Payment.status == PaymentStatus.COMPLETED,
        )
    )
    existing_payment = existing_payment_result.scalar_one_or_none()
    if existing_payment:
        raise HTTPException(
            status_code=400, detail="You have already paid for this course"
        )

    new_payment = Payment(
        user_id=current_user.id,
        course_id=course.id,
        amount=course.price,
        method=payment.method,
        created_at=datetime.utcnow(),
        expiration_date=datetime.utcnow() + timedelta(days=730),  # 2 years
    )
    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)

    # Here you would integrate with a payment gateway
    # For now, we'll just mark it as completed
    new_payment.status = PaymentStatus.COMPLETED
    new_payment.completed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(new_payment)

    return new_payment


@router.get("/history", response_model=List[payment_schema.PaymentResponse])
async def get_payment_history(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Payment).where(Payment.user_id == current_user.id))
    payments = result.scalars().all()
    return payments


@router.post("/refund/{payment_id}", response_model=payment_schema.PaymentResponse)
async def refund_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Payment).where(
            Payment.id == payment_id, Payment.user_id == current_user.id
        )
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.status != PaymentStatus.COMPLETED:
        raise HTTPException(
            status_code=400, detail="Only completed payments can be refunded"
        )

    # Check refund conditions
    if (datetime.utcnow() - payment.completed_at).days > 7:
        raise HTTPException(status_code=400, detail="Refund period has expired")

    # Here you would check the course progress, assuming it's less than 10%

    # Process refund (integrate with payment gateway)
    payment.status = PaymentStatus.REFUNDED
    await db.commit()
    await db.refresh(payment)

    return payment


@router.post("/apply_coupon", response_model=float)
async def apply_coupon(
    course_id: int,
    coupon_code: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    course_result = await db.execute(select(Course).where(Course.id == course_id))
    course = course_result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    coupon_result = await db.execute(
        select(Coupon).where(
            Coupon.code == coupon_code, Coupon.valid_until > datetime.utcnow()
        )
    )
    coupon = coupon_result.scalar_one_or_none()
    if not coupon:
        raise HTTPException(status_code=404, detail="Invalid or expired coupon")

    discounted_price = course.price * (1 - coupon.discount_percent / 100)
    return discounted_price
