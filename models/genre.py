from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel, genre_book_association

if TYPE_CHECKING:
    from models.book import Book


class Genre(BaseModel):
    __tablename__ = "genres"

    name: Mapped[str] = mapped_column(nullable=False)
    books: Mapped[list["Book"]] = relationship(
        "Book",
        secondary=genre_book_association,
        back_populates="genres",
    )

    def __str__(self):
        return self.name
