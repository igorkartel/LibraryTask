from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from models.user_role_enum import UserRoleEnum


class UserBaseSchema(BaseModel):
    id: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class UserCreateSchema(UserBaseSchema):
    name: str
    surname: str
    username: str
    password: str = Field(min_length=8)
    email: EmailStr
    role: UserRoleEnum = UserRoleEnum.LIBRARIAN
    is_blocked: bool = False


class UserReadSchema(UserBaseSchema):
    name: str
    surname: str
    username: str
    email: EmailStr
    role: UserRoleEnum
    is_blocked: bool


class UserUpdateSchema(BaseModel):
    name: str | None = None
    surname: str | None = None
    username: str | None = None
    email: EmailStr | None = None


class UserAdminUpdateSchema(UserUpdateSchema):
    role: UserRoleEnum | None = None
    is_blocked: bool | None = None


class UserDeleteSchema(BaseModel):
    message: str
