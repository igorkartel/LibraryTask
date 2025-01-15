from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DECIMAL, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import (
    BaseModel,
    author_book_association,
    genre_book_association,
    order_book_instance_association,
)

if TYPE_CHECKING:
    from models.author import Author
    from models.genre import Genre
    from models.order import Order


class Book(BaseModel):
    __tablename__ = "books"

    title_rus: Mapped[str] = mapped_column(nullable=False)
    title_origin: Mapped[Optional[str]] = mapped_column(default=None)
    quantity: Mapped[int] = mapped_column(nullable=False, default=0)
    available_for_loan: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(default=None)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    updated_by: Mapped[Optional[str]] = mapped_column(default=None)

    authors: Mapped[list["Author"]] = relationship(
        "Author", secondary=author_book_association, back_populates="books", lazy="joined"
    )
    genres: Mapped[list["Genre"]] = relationship(
        "Genre", secondary=genre_book_association, back_populates="books", lazy="joined"
    )
    instances: Mapped[list["BookInstance"]] = relationship(
        "BookInstance", back_populates="book", lazy="joined"
    )

    def __str__(self):
        return self.title_rus


class BookStatusEnum(str, Enum):
    AVAILABLE = "available"
    LOANED = "loaned"
    LOST = "lost"


class BookInstance(BaseModel):
    __tablename__ = "book_instances"

    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    imprint_year: Mapped[Optional[int]] = mapped_column(default=None)
    pages: Mapped[Optional[int]] = mapped_column(default=None)
    cover_s3_url: Mapped[Optional[str]] = mapped_column(default=None)
    value: Mapped[float] = mapped_column(DECIMAL(precision=10, scale=2), nullable=False)
    price_per_day: Mapped[float] = mapped_column(DECIMAL(precision=10, scale=2), nullable=False)
    status: Mapped[BookStatusEnum] = mapped_column(nullable=False, default=BookStatusEnum.AVAILABLE)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(default=None)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    updated_by: Mapped[Optional[str]] = mapped_column(default=None)

    book = relationship("Book", back_populates="instances", lazy="joined")
    orders: Mapped[List["Order"]] = relationship(
        "Order", secondary=order_book_instance_association, back_populates="book_instances", lazy="joined"
    )

    def __str__(self):
        return f"{self.id}. {self.book.title_rus}, {self.imprint_year}"
