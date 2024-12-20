from datetime import datetime

from fastapi import Form
from pydantic import BaseModel, Field


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


class AuthorUpdateSchema(BaseModel):
    name: str | None = None
    surname: str | None = None
    nationality: str | None = None
    photo_s3_url: str | None = None
    updated_by: str | None = None


class AuthorDeleteSchema(BaseModel):
    message: str
