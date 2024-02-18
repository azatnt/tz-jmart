from fastapi import APIRouter

from src.user import routers as user_router
from src.auth import routers as auth_router

router = APIRouter()

router.include_router(user_router.router, prefix="/user", tags=["user"])
router.include_router(auth_router.router, prefix="/auth", tags=["auth"])
