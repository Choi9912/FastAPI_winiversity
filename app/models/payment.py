from sqlalchemy import Float, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base import Base
import enum
from typing import Optional
from datetime import datetime


class PaymentMethod(enum.Enum):
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    EASY_PAYMENT = "easy_payment"


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("courses.id"))
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    method: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expiration_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    imp_uid: Mapped[str] = mapped_column(String, unique=True, index=True)
    merchant_uid: Mapped[str] = mapped_column(String, unique=True, index=True)

    user: Mapped["User"] = relationship("User", back_populates="payments")
    course: Mapped["Course"] = relationship("Course", back_populates="payments")


class Coupon(Base):
    __tablename__ = "coupons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String, unique=True, index=True)
    discount_percent: Mapped[float] = mapped_column(Float)
    valid_until: Mapped[datetime] = mapped_column(DateTime)
