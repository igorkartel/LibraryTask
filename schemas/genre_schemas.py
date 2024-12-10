from typing import List

from pydantic import BaseModel

from schemas.book_schemas import BookReadSchema


class GenreCreateSchema(BaseModel):
    name: str

    class Config:
        from_attributes = True


class GenreReadSchema(GenreCreateSchema):
    id: int


class GenreWithBooksReadSchema(GenreReadSchema):
    books: List[BookReadSchema] = []


class GenreUpdateSchema(BaseModel):
    name: str | None = None


class GenreDeleteSchema(BaseModel):
    message: str
