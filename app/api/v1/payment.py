from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...db.session import get_async_db
from ...models.user import User
from ...models.courses import Course
from ...models.payment import Coupon, Payment, PaymentStatus
from ...schemas import payment as payment_schema
from ..dependencies import get_current_active_user
from datetime import datetime, timedelta
from typing import List
from sqlalchemy import select
import requests
import time
import uuid

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)

# PortOne 설정
PORTONE_STORE_ID = "store-e05df7ba-b0d4-4c2d-a353-fcec22ab9fd2"
PORTONE_CHANNEL_GROUP_ID = "channel-group-test-3e707d66-6bc1-4843-8e7b-fd09423fb219"
PORTONE_API_URL = "https://api.portone.io/v2"


async def apply_coupon(db: AsyncSession, course_id: int, coupon_code: str) -> float:
    coupon_result = await db.execute(
        select(Coupon).where(
            Coupon.code == coupon_code, Coupon.valid_until > datetime.utcnow()
        )
    )
    coupon = coupon_result.scalar_one_or_none()
    if not coupon:
        return 0.0

    course_result = await db.execute(select(Course).where(Course.id == course_id))
    course = course_result.scalar_one_or_none()
    if not course:
        return 0.0

    discount_amount = course.price * (coupon.discount_percent / 100)
    return discount_amount


@router.post("/prepare", response_model=payment_schema.PaymentPrepareResponse)
async def prepare_payment(
    payment: payment_schema.PaymentPrepareRequest,
    db: AsyncSession = Depends(get_async_db),
):
    course_result = await db.execute(
        select(Course).where(Course.id == payment.course_id)
    )
    course = course_result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    payment_id = f"payment-{uuid.uuid4()}"

    discount_amount = 0.0
    if payment.coupon_code:
        discount_amount = await apply_coupon(db, payment.course_id, payment.coupon_code)

    total_amount = course.price - discount_amount

    customer_info = payment_schema.CustomerInfo(
        customerId="test_user_id",
        fullName="Test User",
        phoneNumber="01012345678",
        email="test@example.com",
    )

    return payment_schema.PaymentPrepareResponse(
        storeId=PORTONE_STORE_ID,
        channelGroupId=PORTONE_CHANNEL_GROUP_ID,
        paymentId=payment_id,
        orderName=course.title,
        totalAmount=total_amount,
        discountAmount=discount_amount,
        currency="KRW",
        payMethod=payment.method,
        customer=customer_info,
    )


@router.post("/confirm", response_model=payment_schema.PaymentResponse)
async def confirm_payment(
    verification: payment_schema.PaymentConfirmRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    # Here you would verify the payment with PortOne API
    # For now, we'll assume the payment is valid

    # Create new payment record
    new_payment = Payment(
        user_id=current_user.id,
        course_id=verification.course_id,
        amount=verification.amount,
        method=verification.method,
        status=PaymentStatus.COMPLETED,
        created_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        expiration_date=datetime.utcnow() + timedelta(days=730),  # 2 years
    )
    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)

    return new_payment


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
