from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError

from configs.logger import logger
from configs.settings import settings
from exception_handlers.author_exc_handlers import (
    AuthorAlreadyExists,
    AuthorDoesNotExist,
)
from models import Author
from repositories.author_repository import AuthorRepository
from schemas.author_schemas import AuthorCreateSchema, AuthorListQueryParams
from usecases.minio_s3_usecases import MinioS3UseCase


class AuthorUseCase:
    def __init__(self, author_repository: AuthorRepository, minio_s3_usecase: MinioS3UseCase):
        self.author_repository = author_repository
        self.minio_s3_usecase = minio_s3_usecase

    async def create_new_author(
        self,
        new_author: AuthorCreateSchema,
        file: UploadFile,
        username: str,
    ):
        try:
            new_authors_surname = new_author.surname.capitalize()
            new_authors_name = new_author.name.capitalize()
            existing_author = await self.author_repository.get_author_by_surname_and_name(
                surname=new_authors_surname, name=new_authors_name
            )
            if existing_author:
                raise AuthorAlreadyExists(
                    message=f"Author '{new_authors_surname} {new_authors_name}' already exists"
                )

            if file:
                authors_bucket = settings.MINIO_BUCKET_NAME_2
                bucket = await self.minio_s3_usecase.ensure_bucket_exists(bucket_name=authors_bucket)

                if not bucket:
                    await self.minio_s3_usecase.create_bucket(bucket_name=authors_bucket)

                file_url = await self.minio_s3_usecase.upload_file_and_get_presigned_url(
                    bucket_name=authors_bucket, file=file
                )
                new_author.photo_s3_url = file_url

            new_author.surname = new_authors_surname
            new_author.name = new_authors_name
            new_author.created_by = username
            new_author = Author(**new_author.model_dump())

            return await self.author_repository.create_new_author(new_author=new_author)

        except SQLAlchemyError as exc:
            logger.error(f"Failed to create a new author: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def get_author_by_id(self, author_id: int):
        try:
            author = await self.author_repository.get_author_by_id(author_id=author_id)

            if not author:
                raise AuthorDoesNotExist(message=f"Author with id '{author_id}' does not exist")

            return author

        except SQLAlchemyError as exc:
            logger.error(f"Failed to fetch author by id: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def get_author_by_surname_and_name(self, surname: str, name: str | None):
        try:
            author = await self.author_repository.get_author_by_surname_and_name(surname=surname, name=name)

            if not author:
                return

            return author

        except SQLAlchemyError as exc:
            logger.error(f"Failed to fetch author by surname and name: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def get_all_authors(self, request_payload: AuthorListQueryParams):
        try:
            return await self.author_repository.get_all_authors(request_payload=request_payload)

        except SQLAlchemyError as exc:
            logger.error(f"Failed to fetch authors' list: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise
