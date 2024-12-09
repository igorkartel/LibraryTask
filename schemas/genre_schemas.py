from typing import List

from pydantic import BaseModel

from schemas.book_schemas import BookReadSchema


class GenreBaseSchema(BaseModel):
    id: int

    class Config:
        from_attributes = True


class GenreCreateSchema(GenreBaseSchema):
    name: str


class GenreReadSchema(GenreCreateSchema):
    pass


class GenreWithBooksReadSchema(GenreReadSchema):
    books: List[BookReadSchema] = []


class GenreUpdateSchema(BaseModel):
    name: str | None = None


class GenreDeleteSchema(BaseModel):
    message: str
