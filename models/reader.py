from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel

if TYPE_CHECKING:
    from models.order import Order


class Reader(BaseModel):
    __tablename__ = "readers"

    name: Mapped[str] = mapped_column(nullable=False)
    fathers_name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    passport_nr: Mapped[Optional[str]] = mapped_column(default=None, unique=True)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="reader")

    def __str__(self):
        return f"{self.surname} {self.name}"
