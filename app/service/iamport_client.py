from iamport import Iamport
from app.core.config import settings

iamport_client = Iamport(
    imp_key=settings.IAMPORT_API_KEY, imp_secret=settings.IAMPORT_API_SECRET
)
