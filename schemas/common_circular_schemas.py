from typing import List

from pydantic import BaseModel

from schemas.author_schemas import AuthorReadSchema
from schemas.book_schemas import (
    BookBaseSchema,
    BookCreateSchema,
    BookInstanceReadSchema,
    BookReadSchema,
)
from schemas.genre_schemas import GenreReadSchema
from schemas.order_schemas import OrderWithoutReaderReadSchema
from schemas.reader_schemas import ReaderReadSchema


class BookWithAuthorsReadSchema(BookCreateSchema, BookBaseSchema):
    id: int
    authors: List[AuthorReadSchema] = []


class BookListSchema(BaseModel):
    books: List[BookWithAuthorsReadSchema]


class BookWithAuthorsGenresReadSchema(BookWithAuthorsReadSchema):
    genres: List[GenreReadSchema] = []


class BookWithInstancesReadSchema(BookWithAuthorsGenresReadSchema):
    instances: List[BookInstanceReadSchema] = []


class AuthorWithBooksReadSchema(AuthorReadSchema):
    books: List[BookReadSchema] = []


class GenreWithBooksReadSchema(GenreReadSchema):
    books: List[BookWithAuthorsReadSchema] = []


class OrderReadSchema(OrderWithoutReaderReadSchema):
    reader: ReaderReadSchema


class ReaderWithOrderSchema(ReaderReadSchema):
    orders: List[OrderWithoutReaderReadSchema] = []
