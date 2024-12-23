from fastapi import UploadFile
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from configs.logger import logger
from configs.settings import settings
from exception_handlers.author_exc_handlers import (
    AuthorAlreadyExists,
    AuthorDoesNotExist,
)
from exception_handlers.minio_s3_exc_handlers import BucketS3DoesNotExist
from models import Author
from repositories.author_repository import AuthorRepository
from schemas.author_schemas import (
    AuthorCreateSchema,
    AuthorListQueryParams,
    AuthorUpdateSchema,
)
from usecases.minio_s3_usecases import MinioS3UseCase


class AuthorUseCase:
    def __init__(self, author_repository: AuthorRepository, minio_s3_usecase: MinioS3UseCase):
        self.author_repository = author_repository
        self.minio_s3_usecase = minio_s3_usecase

    async def create_new_author(
        self,
        new_author: AuthorCreateSchema,
        file: UploadFile | None,
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

            if file and file.filename != "":
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

    async def update_author(
        self, author_id: int, updated_data: AuthorUpdateSchema, file: UploadFile | None, username: str
    ):
        try:
            update_data_dict = updated_data.model_dump(exclude_unset=True, exclude_none=True)

            if updated_data.name:
                update_data_dict["name"] = updated_data.name.capitalize()

            if updated_data.surname:
                update_data_dict["surname"] = updated_data.surname.capitalize()

            update_data_dict["updated_by"] = username

            author_to_update = await self.author_repository.get_author_by_id(author_id=author_id)

            if not author_to_update:
                raise AuthorDoesNotExist(message=f"Author with id '{author_id}' does not exist")

            if file and file.filename != "":
                authors_bucket = settings.MINIO_BUCKET_NAME_2

                if author_to_update.photo_s3_url:
                    bucket = await self.minio_s3_usecase.ensure_bucket_exists(bucket_name=authors_bucket)

                    if not bucket:
                        raise BucketS3DoesNotExist()

                    await self.minio_s3_usecase.delete_file(
                        bucket_name=authors_bucket, filename=author_to_update.photo_s3_url.split("/")[-1]
                    )

                bucket = await self.minio_s3_usecase.ensure_bucket_exists(bucket_name=authors_bucket)

                if not bucket:
                    await self.minio_s3_usecase.create_bucket(bucket_name=authors_bucket)

                file_url = await self.minio_s3_usecase.upload_file_and_get_presigned_url(
                    bucket_name=authors_bucket, file=file
                )
                update_data_dict["photo_s3_url"] = file_url

            for key, value in update_data_dict.items():
                setattr(author_to_update, key, value)

            author_to_update.updated_at = func.now()

            return await self.author_repository.update_author(author_to_update=author_to_update)

        except SQLAlchemyError as exc:
            logger.error(f"Failed to update author: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def delete_author(self, author_id: int):
        try:
            author_to_delete = await self.author_repository.get_author_by_id(author_id=author_id)

            if not author_to_delete:
                raise AuthorDoesNotExist(message=f"Author with id '{author_id}' does not exist")

            if author_to_delete.photo_s3_url:
                authors_bucket = settings.MINIO_BUCKET_NAME_2
                bucket = await self.minio_s3_usecase.ensure_bucket_exists(bucket_name=authors_bucket)

                if not bucket:
                    raise BucketS3DoesNotExist()

                await self.minio_s3_usecase.delete_file(
                    bucket_name=authors_bucket, filename=author_to_delete.photo_s3_url.split("/")[-1]
                )

            return await self.author_repository.delete_author(author_to_delete=author_to_delete)

        except SQLAlchemyError as exc:
            logger.error(f"Failed to delete author: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise
