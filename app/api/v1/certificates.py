from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from ...db.session import get_async_db
from ...models.user import User
from ...api.dependencies import get_current_active_user
from ...services.certificate_service import CertificateService
from ...schemas import certificates as cert_schema

router = APIRouter(prefix="/certificates", tags=["certificates"])

@router.post("/issue/{course_id}", response_model=cert_schema.CertificateInDB)
async def issue_certificate(
    course_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    certificate_service: CertificateService = Depends()
):
    return await certificate_service.issue_certificate(db, current_user.id, course_id)

@router.get("/verify/{certificate_number}", response_model=cert_schema.CertificateVerification)
async def verify_certificate(
    certificate_number: str,
    db: AsyncSession = Depends(get_async_db),
    certificate_service: CertificateService = Depends()
):
    return await certificate_service.verify_certificate(db, certificate_number)