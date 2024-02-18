from fastapi import APIRouter, Depends, Body
from fastapi.security import HTTPBasic
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from src.user import schemas
from src.user.models import User
from src.utils import deps
from src.utils.helpers import validate_not_found, validate_already_exists, hash_password

router = APIRouter()

security = HTTPBasic()


@router.post("/create/")
async def post_create_user(
    db: AsyncSession = Depends(deps.get_db_session),
    data_in: schemas.UserCreate = Body(description="Body of request to create User"),
    current_user: deps.TokenData = Depends(deps.get_current_user)
):
    """create new user instance"""
    await validate_already_exists(
        db,
        model_class=User,
        username=data_in.username,
        email=data_in.email,
    )
    hashed_password = hash_password(data_in.password)
    user_data = data_in.dict()
    user_data.update({"password": hashed_password})
    new_user = await User.create(db, **user_data)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=f"Successfully created user - id={new_user.id}, username={new_user.username}!"
    )


@router.get("/users")
async def get_users(db: AsyncSession = Depends(deps.get_db_session),
                    current_user: deps.TokenData = Depends(deps.get_current_user)
                    ):
    """returns list of users from db"""
    result = await User._select(db)
    users = result.scalars().all()
    return users


@router.get("/{user_id}/")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(deps.get_db_session),
    current_user: deps.TokenData = Depends(deps.get_current_user)
):
    """returns user instance with user information"""
    user = await validate_not_found(db, model_class=User, id=user_id)
    return user
