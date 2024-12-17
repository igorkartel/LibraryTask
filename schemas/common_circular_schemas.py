from typing import List

from schemas.author_schemas import AuthorReadSchema
from schemas.book_schemas import (
    BookCreateSchema,
    BookInstanceReadSchema,
    BookReadSchema,
)
from schemas.genre_schemas import GenreReadSchema
from schemas.order_schemas import OrderWithoutReaderReadSchema
from schemas.reader_schemas import ReaderReadSchema


class BookWithAuthorReadSchema(BookCreateSchema):
    id: int
    authors: List[AuthorReadSchema] = []


class BookWithGenresInstancesReadSchema(BookCreateSchema):
    id: int
    genres: List[GenreReadSchema] = []
    instances: List[BookInstanceReadSchema] = []


class AuthorWithBooksReadSchema(AuthorReadSchema):
    books: List[BookReadSchema] = []


class GenreWithBooksReadSchema(GenreReadSchema):
    books: List[BookWithAuthorReadSchema] = []


class OrderReadSchema(OrderWithoutReaderReadSchema):
    reader: ReaderReadSchema


class ReaderWithOrderSchema(ReaderReadSchema):
    orders: List[OrderWithoutReaderReadSchema] = []
