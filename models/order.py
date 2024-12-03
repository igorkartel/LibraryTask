from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel, order_book_association

if TYPE_CHECKING:
    from models.book import Book
    from models.reader import Reader


class Order(BaseModel):
    __tablename__ = "orders"

    reader_id: Mapped[int] = mapped_column(ForeignKey("readers.id"), nullable=False)
    order_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    return_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_cost: Mapped[float] = mapped_column(DECIMAL(precision=10, scale=2), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    books: Mapped[list["Book"]] = relationship(
        "Book", secondary=order_book_association, back_populates="orders"
    )
    reader: Mapped["Reader"] = relationship("Reader", back_populates="orders")

    __table_args__ = (UniqueConstraint("reader_id", "order_date", name="unique_reader_order"),)
