from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ...db.session import get_async_db
from ...models.courses import Certificate, Course, Enrollment
from ...models.user import User
from ...schemas import certificates as cert_schema
from ...api.dependencies import get_current_active_user
from ...core.pdf_generator import generate_certificate_pdf
import uuid
from datetime import datetime

router = APIRouter()


@router.post("/issue/{course_id}", response_model=cert_schema.CertificateInDB)
async def issue_certificate(
    course_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    # 수료 조건 확인 (예: 모든 레슨 완료)
    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == course_id,
            Enrollment.is_completed == True,
        )
        .first()
    )

    if not enrollment:
        raise HTTPException(status_code=400, detail="Course not completed")

    # 이미 발급된 수료증 확인
    existing_cert = (
        db.query(Certificate)
        .filter(
            Certificate.user_id == current_user.id, Certificate.course_id == course_id
        )
        .first()
    )

    if existing_cert:
        raise HTTPException(status_code=400, detail="Certificate already issued")

    # 새 수료증 생성
    new_cert = Certificate(
        user_id=current_user.id,
        course_id=course_id,
        issue_date=datetime.utcnow(),
        certificate_number=str(uuid.uuid4()),
    )
    db.add(new_cert)
    db.commit()
    db.refresh(new_cert)

    # 백그라운드에서 PDF 생성
    background_tasks.add_task(generate_certificate_pdf, new_cert, current_user, db)

    return new_cert


@router.get("/verify/{certificate_number}")
async def verify_certificate(
    certificate_number: str, db: Session = Depends(get_async_db)
):
    cert = (
        db.query(Certificate)
        .filter(Certificate.certificate_number == certificate_number)
        .first()
    )
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return {"valid": True, "issue_date": cert.issue_date}
