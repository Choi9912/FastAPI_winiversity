from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CertificateBase(BaseModel):
    issue_date: datetime
    certificate_number: str
    model_config = {
        "from_attributes": True
    }


class CertificateCreate(CertificateBase):
    user_id: int
    course_id: int


class CertificateInDB(CertificateBase):
    id: int
    user_id: int
    course_id: int


class CertificateVerification(BaseModel):
    certificate_number: str
    issue_date: datetime
    user_name: str
    course_title: str

    model_config = {"from_attributes": True}
