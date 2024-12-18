from enum import Enum
from typing import List

from fastapi import Query
from pydantic import BaseModel


class GenreCreateSchema(BaseModel):
    name: str

    model_config = {"from_attributes": True}


class GenreReadSchema(GenreCreateSchema):
    id: int


class GenresListSchema(BaseModel):
    genres: List[GenreReadSchema]


class GenreUpdateSchema(BaseModel):
    name: str | None = None


class GenreDeleteSchema(BaseModel):
    message: str


class GenreSortBy(str, Enum):
    id = "id"
    name = "name"


class GenreOrderBy(str, Enum):
    asc = "asc"
    desc = "desc"


class GenreListQueryParams(BaseModel):
    page: int = Query(1, gt=0)
    limit: int = 30
    sort_by: GenreSortBy = GenreSortBy.name
    order_by: GenreOrderBy = GenreOrderBy.asc
