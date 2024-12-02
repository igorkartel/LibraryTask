from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel, author_book_association

if TYPE_CHECKING:
    from models.book import Book


class Author(BaseModel):
    __tablename__ = "authors"

    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    nationality: Mapped[str] = mapped_column(nullable=False)
    photo_s3_url: Mapped[str | None] = mapped_column(default=None)

    books: Mapped[list["Book"]] = relationship(
        "Book",
        secondary=author_book_association,
        back_populates="authors",
    )
