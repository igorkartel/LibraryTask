from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError

from configs.logger import logger
from exception_handlers.book_exc_handlers import BookAlreadyExists
from models import Book
from repositories.book_repository import BookRepository
from schemas.author_schemas import AuthorCreateSchema
from schemas.book_schemas import BookWithAuthorsGenresCreateSchema
from schemas.genre_schemas import GenreCreateSchema
from usecases.author_usecases import AuthorUseCase
from usecases.genre_usecases import GenreUseCase


class BookUseCase:
    def __init__(
        self, book_repository: BookRepository, author_usecase: AuthorUseCase, genre_usecase: GenreUseCase
    ):
        self.book_repository = book_repository
        self.author_usecase = author_usecase
        self.genre_usecase = genre_usecase

    async def create_new_book_with_author_and_genre(
        self,
        new_book: BookWithAuthorsGenresCreateSchema,
        file: UploadFile | None,
        username: str,
    ):
        try:
            author = await self.author_usecase.get_author_by_surname_and_name(
                surname=new_book.authors_surname, name=new_book.authors_name
            )

            if not author:
                new_author = AuthorCreateSchema(
                    name=new_book.authors_name,
                    surname=new_book.authors_surname,
                    nationality=new_book.authors_nationality,
                )

                author = await self.author_usecase.create_new_author(
                    new_author=new_author, file=file, username=username
                )

            genre = await self.genre_usecase.get_genre_by_name(name=new_book.genre_name)

            if not genre:
                new_genre = GenreCreateSchema(name=new_book.genre_name)

                genre = await self.genre_usecase.create_new_genre(new_genre=new_genre)

            book = await self.book_repository.get_book_by_title_and_author(
                title=new_book.title_rus, author=new_book.authors_surname
            )

            if book:
                raise BookAlreadyExists(
                    message=f"The book '{new_book.title_rus}' of the author {new_book.authors_name} {new_book.authors_surname} already exists"
                )

            new_book = Book(
                title_rus=new_book.title_rus,
                title_origin=new_book.title_origin,
                quantity=new_book.quantity,
                available_for_loan=new_book.available_for_loan,
                created_by=username,
            )

            new_book.authors.append(author)
            new_book.genres.append(genre)

            return await self.book_repository.create_new_book_with_author_and_genre(new_book=new_book)

        except SQLAlchemyError as exc:
            logger.error(f"Failed to create a new book: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def get_book_by_title_and_author(self, title: str, author: str):
        try:
            book = await self.book_repository.get_book_by_title_and_author(title=title, author=author)

            if not book:
                return

            return book

        except SQLAlchemyError as exc:
            logger.error(f"Failed to fetch book by title and author: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise
