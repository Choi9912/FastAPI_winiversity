from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.payment import Coupon, Payment, PaymentStatus
from ..models.courses import Course
from ..schemas import payment as payment_schema
from fastapi import HTTPException
from datetime import datetime, timedelta
import uuid
import os
from dotenv import load_dotenv
import requests
from typing import List

load_dotenv()

PORTONE_STORE_ID = os.getenv("PORTONE_STORE_ID")
PORTONE_CHANNEL_GROUP_ID = os.getenv("PORTONE_CHANNEL_GROUP_ID")
PORTONE_API_URL = os.getenv("PORTONE_API_URL")


class PaymentService:
    async def apply_coupon(self, db: AsyncSession, course_id: int, coupon_code: str) -> float:
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

    async def prepare_payment(self, db: AsyncSession, payment: payment_schema.PaymentPrepareRequest) -> payment_schema.PaymentPrepareResponse:
        course_result = await db.execute(
            select(Course).where(Course.id == payment.course_id)
        )
        course = course_result.scalar_one_or_none()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        payment_id = f"payment-{uuid.uuid4()}"

        discount_amount = 0.0
        if payment.coupon_code:
            discount_amount = await self.apply_coupon(db, payment.course_id, payment.coupon_code)

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

    async def confirm_payment(self, db: AsyncSession, user_id: int, verification: payment_schema.PaymentConfirmRequest) -> Payment:
        course_result = await db.execute(select(Course).where(Course.id == verification.course_id))
        course = course_result.scalar_one_or_none()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        new_payment = Payment(
            user_id=user_id,
            course_id=course.id,
            amount=course.price,
            method=verification.method,
            created_at=datetime.utcnow(),
            expiration_date=datetime.utcnow() + timedelta(days=730), 
        )
        db.add(new_payment)
        await db.commit()
        await db.refresh(new_payment)

        new_payment.status = PaymentStatus.COMPLETED
        new_payment.completed_at = datetime.utcnow()
        await db.commit()
        await db.refresh(new_payment)

        return new_payment

    async def get_payment_history(self, db: AsyncSession, user_id: int) -> List[Payment]:
        result = await db.execute(select(Payment).where(Payment.user_id == user_id))
        return result.scalars().all()

    async def refund_payment(self, db: AsyncSession, user_id: int, payment_id: int) -> Payment:
        result = await db.execute(
            select(Payment).where(
                Payment.id == payment_id, Payment.user_id == user_id
            )
        )
        payment = result.scalar_one_or_none()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        if payment.status != PaymentStatus.COMPLETED:
            raise HTTPException(
                status_code=400, detail="Only completed payments can be refunded"
            )

        if (datetime.utcnow() - payment.completed_at).days > 7:
            raise HTTPException(status_code=400, detail="Refund period has expired")

        payment.status = PaymentStatus.REFUNDED
        await db.commit()
        await db.refresh(payment)

        return payment

    async def apply_coupon_to_course(self, db: AsyncSession, course_id: int, coupon_code: str) -> float:
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
