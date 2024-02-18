from typing import TypeVar

from fastapi import HTTPException
from passlib.context import CryptContext
from starlette import status

from src.db.base_model import BaseModel

BaseModelType = TypeVar("BaseModelType")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """function to hash user's password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    """function to verify user's password with hashed"""
    return pwd_context.verify(plain_password, hashed_password)


async def validate_not_found(db, *, model_class: BaseModelType, **kwargs) -> BaseModel:
    """validates instance for existence"""
    instance = await model_class.select_one_or_none(
        db,
        **kwargs,
    )
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found!")
    return instance


async def validate_already_exists(db, *, model_class: BaseModelType, **kwargs) -> None:
    """validates instance to avoid duplicate"""
    instance = await model_class.select_one_or_none(
        db,
        **kwargs,
    )
    if instance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already exists!"
        )