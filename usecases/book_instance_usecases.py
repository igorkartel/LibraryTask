from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError

from configs.logger import logger
from configs.settings import settings
from models import BookInstance
from repositories.book_instance_repository import BookInstanceRepository
from schemas.book_schemas import BookInstanceCreateSchema
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
                new_book_instance=new_book_instance
            )

        except SQLAlchemyError as exc:
            logger.error(f"Failed to create a new book instance: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def get_book_instance_by_id(self, book_instance_id):
        pass

    async def get_all_instances_by_book_title(self, book_title, request_payload):
        pass

    async def update_book_instance(self, book_item_to_update):
        pass

    async def delete_book_instance(self, book_item_to_delete):
        pass
