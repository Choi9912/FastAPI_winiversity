from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.courses import Certificate, Course
from ..models.user import User
from ..schemas import certificates as cert_schema
from fastapi import HTTPException
from datetime import datetime
import uuid
from ..core.pdf_generator import generate_certificate_pdf

class CertificateService:
    async def issue_certificate(self, db: AsyncSession, user_id: int, course_id: int) -> Certificate:
        query = select(Certificate).filter(
            Certificate.user_id == user_id, Certificate.course_id == course_id
        )
        result = await db.execute(query)
        existing_cert = result.scalar_one_or_none()

        if existing_cert:
            raise HTTPException(status_code=400, detail="Certificate already issued")

        new_cert = Certificate(
            user_id=user_id,
            course_id=course_id,
            issue_date=datetime.utcnow(),
            certificate_number=str(uuid.uuid4()),
        )
        db.add(new_cert)
        await db.commit()
        await db.refresh(new_cert)

        course_query = select(Course).filter(Course.id == course_id)
        course_result = await db.execute(course_query)
        course = course_result.scalar_one_or_none()

        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        user_query = select(User).filter(User.id == user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        await generate_certificate_pdf(new_cert, user, course, db)

        return new_cert

    async def verify_certificate(self, db: AsyncSession, certificate_number: str) -> cert_schema.CertificateVerification:
        query = select(Certificate).filter(
            Certificate.certificate_number == certificate_number
        )
        result = await db.execute(query)
        certificate = result.scalar_one_or_none()

        if not certificate:
            raise HTTPException(status_code=404, detail="Certificate not found")

        user_query = select(User).filter(User.id == certificate.user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()

        course_query = select(Course).filter(Course.id == certificate.course_id)
        course_result = await db.execute(course_query)
        course = course_result.scalar_one_or_none()

        user_name = "Unknown"
        if user:
            user_name = user.nickname or user.username or "Unknown"

        return cert_schema.CertificateVerification(
            certificate_number=certificate.certificate_number,
            issue_date=certificate.issue_date,
            user_name=user_name,
            course_title=course.title if course else "Unknown",
        )