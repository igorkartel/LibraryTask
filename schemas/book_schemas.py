from datetime import datetime
from enum import Enum

from fastapi import Form, Query
from pydantic import BaseModel, field_validator

from models.book import BookStatusEnum


class BookBaseSchema(BaseModel):
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BookCreateSchema(BaseModel):
    title_rus: str
    title_origin: str | None = None
    quantity: int = 0
    available_for_loan: int = 0
    created_by: str | None = None
    updated_by: str | None = None


class BookWithAuthorsGenresCreateSchema(BookCreateSchema):
    authors_name: str
    authors_surname: str
    authors_nationality: str
    genre_name: str

    @field_validator(
        "title_rus",
        "title_origin",
        "authors_name",
        "authors_surname",
        "authors_nationality",
        "genre_name",
        mode="before",
    )
    def empty_string_to_none(cls, value):
        if value is None:
            return None
        value = value.strip()
        return None if value == "" else value

    @classmethod
    def as_form(
        cls,
        title_rus: str = Form(),
        title_origin: str | None = Form(default=None),
        quantity: int = Form(default=0),
        available_for_loan: int = Form(default=0),
        created_by: str | None = Form(default=None),
        updated_by: str | None = Form(default=None),
        authors_name: str = Form(),
        authors_surname: str = Form(),
        authors_nationality: str = Form(),
        genre_name: str = Form(),
    ):
        return cls(
            title_rus=title_rus,
            title_origin=title_origin,
            quantity=quantity,
            available_for_loan=available_for_loan,
            created_by=created_by,
            updated_by=updated_by,
            authors_name=authors_name,
            authors_surname=authors_surname,
            authors_nationality=authors_nationality,
            genre_name=genre_name,
        )


class BookInstanceCreateSchema(BaseModel):
    book_id: int = None
    imprint: int = None
    pages: int = None
    cover_s3_url: str = None
    value: float
    price_per_day: float = None
    status: BookStatusEnum = BookStatusEnum.AVAILABLE
    created_by: str = None
    updated_by: str = None

    @classmethod
    def as_form(
        cls,
        book_id: int | None = Form(default=None),
        imprint: int | None = Form(default=None),
        pages: int | None = Form(default=None),
        cover_s3_url: str | None = Form(default=None),
        value: float = Form(),
        price_per_day: float | None = Form(default=None),
        status: BookStatusEnum = Form(default=BookStatusEnum.AVAILABLE),
        created_by: str | None = Form(default=None),
        updated_by: str | None = Form(default=None),
    ):
        return cls(
            book_id=book_id,
            imprint=imprint,
            pages=pages,
            cover_s3_url=cover_s3_url,
            value=value,
            price_per_day=price_per_day,
            status=status,
            created_by=created_by,
            updated_by=updated_by,
        )


class BookReadSchema(BookCreateSchema, BookBaseSchema):
    id: int


class BookInstanceReadSchema(BookInstanceCreateSchema, BookBaseSchema):
    id: int
    imprint: int
    pages: int
    cover_s3_url: str
    value: float
    price_per_day: float
    status: BookStatusEnum


class BookInstanceWithBookReadSchema(BookInstanceReadSchema):
    book: BookReadSchema


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
    updated_by: str | None = None

    @classmethod
    def as_form(
        cls,
        imprint: int | None = Form(default=None),
        pages: int | None = Form(default=None),
        cover_s3_url: str | None = Form(default=None),
        value: float | None = Form(default=None),
        price_per_day: float | None = Form(default=None),
        status: BookStatusEnum = Form(default=None),
        updated_by: str | None = Form(default=None),
    ):
        return cls(
            imprint=imprint,
            pages=pages,
            cover_s3_url=cover_s3_url,
            value=value,
            price_per_day=price_per_day,
            status=status,
            updated_by=updated_by,
        )


class BookDeleteSchema(BaseModel):
    message: str


class BookInstanceDeleteSchema(BookDeleteSchema):
    pass


class BookSortBy(str, Enum):
    id = "id"
    title_rus = "title_rus"


class BookOrderBy(str, Enum):
    asc = "asc"
    desc = "desc"


class BookListQueryParams(BaseModel):
    page: int = Query(1, gt=0)
    limit: int = 30
    sort_by: BookSortBy = BookSortBy.title_rus
    order_by: BookOrderBy = BookOrderBy.asc
