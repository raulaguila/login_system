from datetime import datetime
from pydantic import BaseModel, EmailStr, constr


class UserBaseSchema(BaseModel):
    name: constr(min_length=10)
    email: EmailStr
    photo: str | None = None
    role: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        orm_mode = True


class CreateUserSchema(UserBaseSchema):
    password: constr(min_length=8)
    passwordConfirm: str
    verified: bool = False


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class UserResponseSchema(UserBaseSchema):
    id: str
