from pydantic import EmailStr, Field, BaseModel


class UserBase(BaseModel):
    username: str = Field(description="Unique username of user")
    email: EmailStr = Field(description="Email of user")


class UserCreate(UserBase):
    password: str = Field(description="Password of user")
