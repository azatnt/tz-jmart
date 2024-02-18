from datetime import timedelta, datetime
from typing import Generator, Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette import status

from src.core.config import settings
from src.db.session import Session
from src.user import User
from src.utils.helpers import hash_password, verify_password

security = HTTPBasic()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_db_session() -> Generator:
    async with Session() as session:
        yield session


class TokenData(BaseModel):
    username: Optional[str] = None


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return token_data


async def create_superuser(**kwargs):
    async with Session() as session:
        stmt = select(User).where((User.username == kwargs.get('username')) | (User.email == kwargs.get('email')))

        result = await session.execute(stmt)
        existing_user = result.scalars().first()
        if not existing_user:
            hashed_password = hash_password(kwargs.get('password'))
            kwargs.update({"password": hashed_password})
            superuser = User(**kwargs)

            session.add(superuser)
            await session.commit()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await User.select_one_or_none(db, username=username)
    if user and verify_password(password, user.password):
        return user
    return None


def create_tokens(user_id: str):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id}, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=7)
    refresh_token = create_access_token(
        data={"sub": user_id}, expires_delta=refresh_token_expires
    )

    return access_token, refresh_token
