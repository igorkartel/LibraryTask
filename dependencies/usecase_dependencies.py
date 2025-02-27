from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.db_dependency import db_session
from dependencies.minio_s3_dependency import get_minio_s3_usecase
from repositories.author_repository import AuthorRepository
from repositories.book_instance_repository import BookInstanceRepository
from repositories.book_repository import BookRepository
from repositories.genre_repository import GenreRepository
from repositories.user_repository import UserRepository
from usecases.auth_usecases import AuthUseCase
from usecases.author_usecases import AuthorUseCase
from usecases.book_instance_usecases import BookInstanceUseCase
from usecases.book_usecases import BookUseCase
from usecases.genre_usecases import GenreUseCase
from usecases.minio_s3_usecases import MinioS3UseCase
from usecases.user_usecases import UserUseCase


async def get_auth_usecase(db: AsyncSession = Depends(db_session)) -> AuthUseCase:
    user_repository = UserRepository(db)
    return AuthUseCase(user_repository)


async def get_user_usecase(db: AsyncSession = Depends(db_session)) -> UserUseCase:
    user_repository = UserRepository(db)
    return UserUseCase(user_repository)


async def get_author_usecase(
    db: AsyncSession = Depends(db_session), minio_s3_usecase: MinioS3UseCase = Depends(get_minio_s3_usecase)
) -> AuthorUseCase:
    author_repository = AuthorRepository(db)
    return AuthorUseCase(author_repository, minio_s3_usecase)


async def get_genre_usecase(db: AsyncSession = Depends(db_session)) -> GenreUseCase:
    genre_repository = GenreRepository(db)
    return GenreUseCase(genre_repository)


# TODO добавить потом book_instance_usecase
async def get_book_usecase(
    db: AsyncSession = Depends(db_session),
    author_usecase: AuthorUseCase = Depends(get_author_usecase),
    genre_usecase: GenreUseCase = Depends(get_genre_usecase),
) -> BookUseCase:
    book_repository = BookRepository(db)
    return BookUseCase(book_repository, author_usecase, genre_usecase)


# TODO добавить потом order_usecase
async def get_book_instance_usecase(
    db: AsyncSession = Depends(db_session),
    book_usecase: BookUseCase = Depends(get_book_usecase),
    minio_s3_usecase: MinioS3UseCase = Depends(get_minio_s3_usecase),
) -> BookInstanceUseCase:
    book_instance_repository = BookInstanceRepository(db)
    return BookInstanceUseCase(book_instance_repository, book_usecase, minio_s3_usecase)
