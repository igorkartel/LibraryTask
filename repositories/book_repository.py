from sqlalchemy import select
from sqlalchemy.orm import joinedload

from exception_handlers.book_exc_handlers import BookDoesNotExist
from models import Author, Book
from repositories.abstract_repositories import AbstractBookRepository
from schemas.common_circular_schemas import BookListSchema, BookWithAuthorsReadSchema


class BookRepository(AbstractBookRepository):
    async def create_new_book(self, new_book):
        pass

    async def create_new_book_with_author_and_genre(self, new_book: Book) -> Book:
        self.db.add(new_book)
        await self.db.commit()
        await self.db.refresh(new_book)
        return new_book

    async def get_book_by_id(self, book_id: int) -> Book | None:
        result = await self.db.execute(
            select(Book).options(joinedload(Book.authors), joinedload(Book.genres)).where(Book.id == book_id)
        )
        book = result.unique().scalars().first()

        return book if book else None

    async def get_books_by_title(self, book_title: str) -> BookListSchema:
        result = await self.db.execute(
            select(Book).options(joinedload(Book.authors)).where(Book.title_rus == book_title)
        )
        books = result.unique().scalars().all()

        if not books:
            raise BookDoesNotExist(message="No books found")

        books = [BookWithAuthorsReadSchema.model_validate(book) for book in books]

        return BookListSchema(books=books)

    async def get_book_by_title_and_author(self, title: str, author: str) -> Book | None:
        result = await self.db.execute(
            select(Book).where(Book.title_rus == title).join(Book.authors).where(Author.surname == author)
        )
        book = result.unique().scalars().first()

        return book if book else None

    async def get_all_books(self, request_payload):
        pass

    async def update_book(self, book_to_update):
        pass

    async def delete_book(self, book_to_delete):
        pass
