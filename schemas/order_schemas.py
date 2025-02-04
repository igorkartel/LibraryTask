from datetime import date
from typing import List

from pydantic import BaseModel, Field

from models.order import OrderStatusEnum
from schemas.book_schemas import BookInstanceReadSchema


class OrderCreateSchema(BaseModel):
    reader_id: int
    order_date: date = Field(default_factory=date.today)
    status: OrderStatusEnum = OrderStatusEnum.ACTIVE
    planned_return_date: date
    fact_return_date: date = None
    overdue_cost: float = 0
    damaged_books: int = 0
    damage_cost: float = 0
    lost_books: int = 0
    lost_cost: float = 0
    total_cost: float = 0
    created_by: str = None
    closed_by: str = None

    model_config = {"from_attributes": True}


class OrderWithoutReaderReadSchema(BaseModel):
    id: int
    order_date: date
    status: OrderStatusEnum
    planned_return_date: date
    fact_return_date: date
    overdue_cost: float
    damaged_books: int
    damage_cost: float
    lost_books: int
    lost_cost: float
    total_cost: float
    book_instances: List[BookInstanceReadSchema]


class OrderUpdateSchema(BaseModel):
    order_date: date | None = None
    status: OrderStatusEnum | None = None
    planned_return_date: date | None = None
    fact_return_date: date | None = None
    overdue_cost: float | None = None
    damaged_books: int | None = None
    damage_cost: float | None = None
    lost_books: int | None = None
    lost_cost: float | None = None
    total_cost: float | None = None


class OrderDeleteSchema(BaseModel):
    message: str
