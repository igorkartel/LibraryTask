from datetime import datetime
from enum import Enum
from typing import List

from fastapi import Form, Query
from pydantic import BaseModel


class AuthorBaseSchema(BaseModel):
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AuthorCreateSchema(BaseModel):
    name: str
    surname: str
    nationality: str
    photo_s3_url: str | None = None
    created_by: str | None = None
    updated_by: str | None = None

    @classmethod
    def as_form(
        cls,
        name: str = Form(),
        surname: str = Form(),
        nationality: str = Form(),
        photo_s3_url: str | None = Form(default=None),
        created_by: str | None = Form(default=None),
        updated_by: str | None = Form(default=None),
    ):
        return cls(
            name=name,
            surname=surname,
            nationality=nationality,
            photo_s3_url=photo_s3_url,
            created_by=created_by,
            updated_by=updated_by,
        )


class AuthorReadSchema(AuthorCreateSchema, AuthorBaseSchema):
    id: int


class AuthorsListSchema(BaseModel):
    authors: List[AuthorReadSchema]


class AuthorUpdateSchema(BaseModel):
    name: str | None = None
    surname: str | None = None
    nationality: str | None = None
    photo_s3_url: str | None = None
    updated_by: str | None = None

    @classmethod
    def as_form(
        cls,
        name: str | None = Form(),
        surname: str | None = Form(),
        nationality: str | None = Form(),
        photo_s3_url: str | None = Form(default=None),
        updated_by: str | None = Form(default=None),
    ):
        return cls(
            name=name,
            surname=surname,
            nationality=nationality,
            photo_s3_url=photo_s3_url,
            updated_by=updated_by,
        )


class AuthorDeleteSchema(BaseModel):
    message: str


class AuthorSortBy(str, Enum):
    id = "id"
    surname = "surname"
    nationality = "nationality"


class AuthorOrderBy(str, Enum):
    asc = "asc"
    desc = "desc"


class AuthorListQueryParams(BaseModel):
    page: int = Query(1, gt=0)
    limit: int = 30
    sort_by: AuthorSortBy = AuthorSortBy.surname
    order_by: AuthorOrderBy = AuthorOrderBy.asc
