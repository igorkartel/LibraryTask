from fastapi import UploadFile
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from configs.logger import logger
from configs.settings import settings
from exception_handlers.book_exc_handlers import BookDoesNotExist
from exception_handlers.minio_s3_exc_handlers import BucketS3DoesNotExist
from models import BookInstance
from repositories.book_instance_repository import BookInstanceRepository
from schemas.book_schemas import BookInstanceCreateSchema, BookInstanceUpdateSchema
from usecases.book_usecases import BookUseCase
from usecases.minio_s3_usecases import MinioS3UseCase


class BookInstanceUseCase:
    def __init__(
        self,
        book_instance_repository: BookInstanceRepository,
        book_usecase: BookUseCase,
        minio_s3_usecase: MinioS3UseCase,
    ):
        self.book_instance_repository = book_instance_repository
        self.book_usecase = book_usecase
        self.minio_s3_usecase = minio_s3_usecase

    async def create_new_book_instance(
        self,
        book_id: int,
        new_book_instance: BookInstanceCreateSchema,
        file: UploadFile | None,
        username: str,
    ):
        try:
            book = await self.book_usecase.get_book_by_id(book_id=book_id)

            if file and file.filename != "":
                books_bucket = settings.MINIO_BUCKET_NAME_1
                bucket = await self.minio_s3_usecase.ensure_bucket_exists(bucket_name=books_bucket)

                if not bucket:
                    await self.minio_s3_usecase.create_bucket(bucket_name=books_bucket)

                file_url = await self.minio_s3_usecase.upload_file_and_get_presigned_url(
                    bucket_name=books_bucket, file=file
                )
                new_book_instance.cover_s3_url = file_url

            new_book_instance.book_id = book.id
            new_book_instance.price_per_day = new_book_instance.value / 30
            new_book_instance.created_by = username
            new_book_instance = BookInstance(**new_book_instance.model_dump())

            return await self.book_instance_repository.create_new_book_instance(
                book=book, new_book_instance=new_book_instance
            )

        except SQLAlchemyError as exc:
            logger.error(f"Failed to create a new book instance: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def get_book_instance_by_id(self, book_instance_id: int):
        try:
            book_instance = await self.book_instance_repository.get_book_instance_by_id(
                book_instance_id=book_instance_id
            )

            if not book_instance:
                raise BookDoesNotExist(message=f"Book item with id '{book_instance_id}' does not exist")

            return book_instance

        except SQLAlchemyError as exc:
            logger.error(f"Failed to fetch book item by id: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def get_all_instances_by_book_id(self, book_id: int):
        try:
            book_with_instances = await self.book_instance_repository.get_all_instances_by_book_id(
                book_id=book_id
            )

            if not book_with_instances:
                raise BookDoesNotExist(message=f"Book with id '{book_id}' does not exist")

            return book_with_instances

        except SQLAlchemyError as exc:
            logger.error(f"Failed to fetch all book instances by book id: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def update_book_instance(
        self,
        book_instance_id: int,
        book_item_to_update: BookInstanceUpdateSchema,
        file: UploadFile | None,
        username: str,
    ):
        try:
            book_instance_to_update = await self.book_instance_repository.get_book_instance_by_id(
                book_instance_id=book_instance_id
            )

            if not book_instance_to_update:
                raise BookDoesNotExist(message=f"Book item with id '{book_instance_id}' does not exist")

            update_data_dict = book_item_to_update.model_dump(exclude_unset=True, exclude_none=True)

            update_data_dict["updated_by"] = username

            if book_item_to_update.value:
                update_data_dict["price_per_day"] = book_item_to_update.value / 30

            if file and file.filename != "":
                books_bucket = settings.MINIO_BUCKET_NAME_1

                if book_instance_to_update.cover_s3_url:
                    bucket = await self.minio_s3_usecase.ensure_bucket_exists(bucket_name=books_bucket)

                    if not bucket:
                        raise BucketS3DoesNotExist()

                    await self.minio_s3_usecase.delete_file(
                        bucket_name=books_bucket,
                        filename=book_instance_to_update.cover_s3_url.split("/")[-1],
                    )

                bucket = await self.minio_s3_usecase.ensure_bucket_exists(bucket_name=books_bucket)

                if not bucket:
                    await self.minio_s3_usecase.create_bucket(bucket_name=books_bucket)

                file_url = await self.minio_s3_usecase.upload_file_and_get_presigned_url(
                    bucket_name=books_bucket, file=file
                )
                update_data_dict["cover_s3_url"] = file_url

            for key, value in update_data_dict.items():
                setattr(book_instance_to_update, key, value)

            book_instance_to_update.updated_at = func.now()

            book = await self.book_usecase.get_book_by_id(book_id=book_instance_to_update.book_id)

            return await self.book_instance_repository.update_book_instance(
                book=book, book_item_to_update=book_instance_to_update
            )

        except SQLAlchemyError as exc:
            logger.error(f"Failed to update book item: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def delete_book_instance(self, book_instance_id: int):
        try:
            book_instance_to_delete = await self.book_instance_repository.get_book_instance_by_id(
                book_instance_id=book_instance_id
            )

            if not book_instance_to_delete:
                raise BookDoesNotExist(message=f"Book item with id '{book_instance_id}' does not exist")

            if book_instance_to_delete.cover_s3_url:
                books_bucket = settings.MINIO_BUCKET_NAME_1
                bucket = await self.minio_s3_usecase.ensure_bucket_exists(bucket_name=books_bucket)

                if not bucket:
                    raise BucketS3DoesNotExist()

                await self.minio_s3_usecase.delete_file(
                    bucket_name=books_bucket, filename=book_instance_to_delete.cover_s3_url.split("/")[-1]
                )

            book = await self.book_usecase.get_book_by_id(book_id=book_instance_to_delete.book_id)

            return await self.book_instance_repository.delete_book_instance(
                book=book, book_item_to_delete=book_instance_to_delete
            )

        except SQLAlchemyError as exc:
            logger.error(f"Failed to delete book instance: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise
