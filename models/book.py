from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DECIMAL, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import (
    BaseModel,
    author_book_association,
    genre_book_association,
    order_book_association,
)

if TYPE_CHECKING:
    from models.author import Author
    from models.genre import Genre
    from models.loan import Loan
    from models.order import Order


class Book(BaseModel):
    __tablename__ = "books"

    title_rus: Mapped[str] = mapped_column(nullable=False)
    title_origin: Mapped[Optional[str]] = mapped_column(default=None)
    imprint_year: Mapped[int] = mapped_column(default=None)
    pages: Mapped[int] = mapped_column(default=None)
    cover_s3_url: Mapped[Optional[str]] = mapped_column(default=None)
    value: Mapped[float] = mapped_column(DECIMAL(precision=10, scale=2), nullable=False)
    price_per_day: Mapped[float] = mapped_column(DECIMAL(precision=10, scale=2), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    authors: Mapped[list["Author"]] = relationship(
        "Author",
        secondary=author_book_association,
        back_populates="books",
    )
    genres: Mapped[list["Genre"]] = relationship(
        "Genre",
        secondary=genre_book_association,
        back_populates="books",
    )
    loans: Mapped[list["Loan"]] = relationship("Loan", back_populates="book")
    orders: Mapped[list["Order"]] = relationship(
        "Order", secondary=order_book_association, back_populates="books"
    )

    def __str__(self):
        return self.title_rus
