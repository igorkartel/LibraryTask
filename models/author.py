from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel, author_book_association

if TYPE_CHECKING:
    from models.book import Book


class Author(BaseModel):
    __tablename__ = "authors"

    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    nationality: Mapped[str] = mapped_column(nullable=False)
    photo_s3_url: Mapped[Optional[str]] = mapped_column(default=None)
    books: Mapped[list["Book"]] = relationship(
        "Book",
        secondary=author_book_association,
        back_populates="authors",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    def __str__(self):
        return f"{self.name} {self.surname}"
