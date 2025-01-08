from fastapi import UploadFile
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from configs.logger import logger
from exception_handlers.book_exc_handlers import BookAlreadyExists, BookDoesNotExist
from models import Book
from repositories.book_repository import BookRepository
from schemas.author_schemas import AuthorCreateSchema
from schemas.book_schemas import (
    BookListQueryParams,
    BookUpdateSchema,
    BookWithAuthorsGenresCreateSchema,
)
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

    async def get_book_by_id(self, book_id: int):
        try:
            book = await self.book_repository.get_book_by_id(book_id=book_id)

            if not book:
                raise BookDoesNotExist(message=f"Book with id '{book_id}' does not exist")

            return book

        except SQLAlchemyError as exc:
            logger.error(f"Failed to fetch book by id: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def get_books_by_title(self, book_title: str):
        try:
            books = await self.book_repository.get_books_by_title(book_title=book_title)

            return books

        except SQLAlchemyError as exc:
            logger.error(f"Failed to fetch book by title: {str(exc)}")
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

    async def get_all_books(self, request_payload: BookListQueryParams):
        try:
            return await self.book_repository.get_all_books(request_payload=request_payload)

        except SQLAlchemyError as exc:
            logger.error(f"Failed to fetch books' list: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def update_book(self, book_id: int, updated_data: BookUpdateSchema, username: str):
        try:
            book_to_update = await self.book_repository.get_book_by_id(book_id=book_id)

            if not book_to_update:
                raise BookDoesNotExist(message=f"Book with id '{book_id}' does not exist")

            update_data_dict = updated_data.model_dump(exclude_unset=True)

            if updated_data.title_rus:
                update_data_dict["title_rus"] = updated_data.title_rus.capitalize()

            if updated_data.title_origin:
                update_data_dict["title_origin"] = updated_data.title_origin.title()

            update_data_dict["updated_by"] = username

            for key, value in update_data_dict.items():
                setattr(book_to_update, key, value)

            book_to_update.updated_at = func.now()

            return await self.book_repository.update_book(book_to_update=book_to_update)

        except SQLAlchemyError as exc:
            logger.error(f"Failed to update book: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def delete_book(self, book_id: int):
        try:
            book_to_delete = await self.book_repository.get_book_by_id(book_id=book_id)

            if not book_to_delete:
                raise BookDoesNotExist(message=f"Book with id '{book_id}' does not exist")

            return await self.book_repository.delete_book(book_to_delete=book_to_delete)

        except SQLAlchemyError as exc:
            logger.error(f"Failed to delete book: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise
