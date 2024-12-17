from datetime import date, datetime
from typing import Annotated, List

from pydantic import BaseModel, EmailStr, Field

from schemas.order_schemas import OrderWithoutReaderReadSchema


class ReaderBaseSchema(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = {"from_attributes": True}


class ReaderCreateSchema(ReaderBaseSchema):
    name: str
    fathers_name: str
    surname: str
    passport_nr: str = None
    date_of_birth: date
    email: EmailStr
    address: str


class ReaderReadSchema(ReaderCreateSchema):
    id: int


class ReaderWithOrderSchema(ReaderReadSchema):
    orders: Annotated[List[OrderWithoutReaderReadSchema], Field(default_factory=list)]


class ReaderUpdateSchema(BaseModel):
    name: str | None = None
    fathers_name: str | None = None
    surname: str | None = None
    passport_nr: str | None = None
    date_of_birth: date | None = None
    email: EmailStr | None = None
    address: str | None = None


class ReaderDeleteSchema(BaseModel):
    message: str
