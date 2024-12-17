from typing import Annotated, List

from pydantic import BaseModel, Field

from schemas.book_schemas import BookReadSchema


class GenreCreateSchema(BaseModel):
    name: str

    model_config = {"from_attributes": True}


class GenreReadSchema(GenreCreateSchema):
    id: int


class GenreWithBooksReadSchema(GenreReadSchema):
    books: Annotated[List[BookReadSchema], Field(default_factory=list)]


class GenreUpdateSchema(BaseModel):
    name: str | None = None


class GenreDeleteSchema(BaseModel):
    message: str
