from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel, author_book_association, genre_book_association

if TYPE_CHECKING:
    from models.author import Author
    from models.genre import Genre


class Book(BaseModel):
    __tablename__ = "books"

    title_rus: Mapped[str] = mapped_column(nullable=False)
    title_origin: Mapped[str | None] = mapped_column(default=None)
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
