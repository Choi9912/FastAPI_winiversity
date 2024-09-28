# 모든 API 버전의 라우터를 여기서 임포트
from .auth import router as auth_router
from .users import router as users_router
from .admin import router as admin_router

__all__ = ["auth_router", "users_router", "admin_router"]
