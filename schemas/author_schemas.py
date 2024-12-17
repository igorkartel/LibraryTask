from datetime import datetime
from typing import Annotated, List

from pydantic import BaseModel, Field

from schemas.book_schemas import BookReadSchema


class AuthorBaseSchema(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = {"from_attributes": True}


class AuthorCreateSchema(AuthorBaseSchema):
    name: str
    surname: str
    nationality: str
    photo_s3_url: str = None


class AuthorReadSchema(AuthorCreateSchema):
    id: int


class AuthorWithBooksReadSchema(AuthorReadSchema):
    books: Annotated[List[BookReadSchema], Field(default_factory=list)]


class AuthorUpdateSchema(BaseModel):
    name: str | None = None
    surname: str | None = None
    nationality: str | None = None
    photo_s3_url: str | None = None


class AuthorDeleteSchema(BaseModel):
    message: str
