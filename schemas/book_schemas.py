from datetime import datetime
from typing import Annotated, Dict, List

from pydantic import BaseModel, Field

from models.book import BookStatusEnum
from schemas.author_schemas import AuthorReadSchema
from schemas.genre_schemas import GenreReadSchema


class BookBaseSchema(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = {"from_attributes": True}


class BookCreateSchema(BookBaseSchema):
    title_rus: str
    title_origin: str = None
    quantity: int = 0
    available_for_loan: int = 0


class BookInstanceCreateSchema(BookBaseSchema):
    book_id: int
    imprint: int = None
    pages: int = None
    cover_s3_url: str = None
    value: float
    price_per_day: float
    status: BookStatusEnum = BookStatusEnum.AVAILABLE


class BookReadSchema(BookCreateSchema):
    id: int
    authors: Annotated[List[AuthorReadSchema], Field(default_factory=list)]


class BookInstanceReadSchema(BaseModel):
    id: int
    imprint: int
    pages: int
    cover_s3_url: str
    value: float
    price_per_day: float
    status: BookStatusEnum


class BookWithGenresInstancesReadSchema(BookCreateSchema):
    id: int
    genres: Annotated[List[GenreReadSchema], Field(default_factory=list)]
    instances: Annotated[List[BookInstanceReadSchema], Field(default_factory=list)]


class BookInstanceWithBookReadSchema(BookInstanceReadSchema):
    book: Annotated[Dict[BookReadSchema], Field(default_factory=dict)]


class BookUpdateSchema(BaseModel):
    title_rus: str | None = None
    title_origin: str | None = None
    quantity: int | None = None
    available_for_loan: int | None = None


class BookInstanceUpdateSchema(BaseModel):
    imprint: int | None = None
    pages: int | None = None
    cover_s3_url: str | None = None
    value: float | None = None
    price_per_day: float | None = None
    status: BookStatusEnum | None = None


class BookDeleteSchema(BaseModel):
    message: str


class BookInstanceDeleteSchema(BookDeleteSchema):
    pass
