import os

from datetime import datetime
from pydantic import BaseModel, constr


MIN_PASS_LENGTH = int(os.getenv('MIN_PASS_LENGTH') if os.getenv('MIN_PASS_LENGTH') else 8)
MIN_NAME_LENGTH = int(os.getenv('MIN_NAME_LENGTH') if os.getenv('MIN_NAME_LENGTH') else 10)
MIN_USER_LENGTH = int(os.getenv('MIN_USER_LENGTH') if os.getenv('MIN_USER_LENGTH') else 5)


class UserBaseSchema(BaseModel):
    name: constr(min_length=MIN_NAME_LENGTH)
    username: constr(min_length=MIN_USER_LENGTH)
    role: str
    status: bool
    email: str | None = None
    photo: str | None = None
    # verified: bool = False

    class Config:
        orm_mode = True


class ResponseUserBaseSchema(UserBaseSchema):
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CreateUserSchema(UserBaseSchema):
    password: constr(min_length=MIN_PASS_LENGTH)
    passwordConfirm: str


class UpdateUserSchema(UserBaseSchema):
    password: constr(min_length=MIN_PASS_LENGTH) | None = None
    passwordConfirm: str | None = None


class LoginUserSchema(BaseModel):
    username: constr(min_length=MIN_USER_LENGTH)
    password: constr(min_length=MIN_PASS_LENGTH)


class UserResponseSchema(ResponseUserBaseSchema):
    id: str
