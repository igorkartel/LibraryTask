from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel

if TYPE_CHECKING:
    from models.book import Book
    from models.reader import Reader


class Loan(BaseModel):
    __tablename__ = "loans"

    reader_id: Mapped[int] = mapped_column(ForeignKey("readers.id"), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    reader: Mapped["Reader"] = relationship("Reader", back_populates="loans")
    book: Mapped["Book"] = relationship("Book", back_populates="loans")

    __table_args__ = (UniqueConstraint("reader_id", "book_id", name="unique_reader_book"),)
