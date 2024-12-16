from datetime import datetime
from enum import Enum
from typing import List

from fastapi import Query
from pydantic import BaseModel, EmailStr, Field

from models.user_role_enum import UserRoleEnum


class UserBaseSchema(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = {"from_attributes": True}


class UserCreateSchema(UserBaseSchema):
    name: str
    surname: str
    username: str
    password: str = Field(min_length=8)
    email: EmailStr
    role: UserRoleEnum = UserRoleEnum.LIBRARIAN
    is_blocked: bool = False


class UserReadSchema(UserBaseSchema):
    id: int
    name: str
    surname: str
    username: str
    email: EmailStr
    role: UserRoleEnum
    is_blocked: bool


class UsersListSchema(BaseModel):
    users: List[UserReadSchema]


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


class UserSortBy(str, Enum):
    id = "id"
    name = "name"
    surname = "surname"
    username = "username"
    email = "email"
    role = "role"
    is_blocked = "is_blocked"
    created_at = "created_at"
    modified_at = "modified_at"


class UserOrderBy(str, Enum):
    asc = "asc"
    desc = "desc"


class UserListQueryParams(BaseModel):
    page: int = Query(1, gt=0)
    limit: int = 30
    sort_by: UserSortBy = UserSortBy.username
    order_by: UserOrderBy = UserOrderBy.asc
