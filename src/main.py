from fastapi import FastAPI

from src.core.config import get_settings
from src.routers import router
from src.utils.deps import create_superuser

settings = get_settings()

app_configs = {"title": settings.APP_NAME}

app = FastAPI(**app_configs)

app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Example usage: create a superuser based on some predefined settings"""
    await create_superuser(
        username=settings.SUPERUSER_USERNAME,
        email=settings.SUPERUSER_EMAIL,
        password=settings.SUPERUSER_PASSWORD,
    )
