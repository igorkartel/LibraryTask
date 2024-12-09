from datetime import date
from enum import Enum
from typing import TYPE_CHECKING, List

from sqlalchemy import DECIMAL, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel, order_book_instance_association

if TYPE_CHECKING:
    from models.book import BookInstance
    from models.reader import Reader


class OrderStatusEnum(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"


class Order(BaseModel):
    __tablename__ = "orders"

    reader_id: Mapped[int] = mapped_column(ForeignKey("readers.id"), nullable=False)
    order_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    status: Mapped[OrderStatusEnum] = mapped_column(nullable=False, default=OrderStatusEnum.ACTIVE)
    planned_return_date: Mapped[date] = mapped_column(Date, nullable=False)
    fact_return_date: Mapped[date] = mapped_column(Date, default=None)
    overdue_cost: Mapped[float] = mapped_column(DECIMAL(precision=10, scale=2), nullable=False, default=0)
    damaged_books: Mapped[int] = mapped_column(nullable=False, default=0)
    damage_cost: Mapped[float] = mapped_column(DECIMAL(precision=10, scale=2), nullable=False, default=0)
    lost_books: Mapped[int] = mapped_column(nullable=False, default=0)
    lost_cost: Mapped[float] = mapped_column(DECIMAL(precision=10, scale=2), nullable=False, default=0)
    total_cost: Mapped[float] = mapped_column(DECIMAL(precision=10, scale=2), nullable=False)

    book_instances: Mapped[List["BookInstance"]] = relationship(
        "BookInstance",
        secondary=order_book_instance_association,
        back_populates="orders",
    )
    reader: Mapped["Reader"] = relationship("Reader", back_populates="orders")

    def __str__(self):
        return f"Заказ №{self.id}_{self.reader.surname}_{self.order_date}"
