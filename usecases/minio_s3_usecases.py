from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile

from configs.logger import logger
from configs.settings import settings
from exception_handlers.minio_s3_exc_handlers import S3OperationException
from repositories.minio_s3_repository import MinioS3Repository


class MinioS3UseCase:
    def __init__(self, minio_s3_repository: MinioS3Repository):
        self.minio_s3_repository = minio_s3_repository

    async def ensure_bucket_exists(self, bucket_name: str) -> bool:
        """
        Checks if the specified bucket exists.

            Params:
                bucket_name (str): The name of the bucket.

            Returns:
                bool: True if bucket exists, False if not.
        """
        try:
            await self.minio_s3_repository.ensure_bucket_exists(bucket_name=bucket_name)
            return True

        except ClientError as exc:
            if exc.response["Error"]["Code"] == "404":
                return False
            else:
                raise S3OperationException(message=f"Failed to check a bucket '{bucket_name}': {str(exc)}")
        except Exception as exc:
            logger.error(str(exc))
            raise S3OperationException(
                message=f"An error occurred while checking a bucket '{bucket_name}': {str(exc)}"
            )

    async def create_bucket(self, bucket_name: str) -> bool:
        """
        Creates a new bucket.

            Params:
                bucket_name (str): The name of the bucket.

            Returns:
                bool: True if bucket is created successfully.
        """
        try:
            await self.minio_s3_repository.create_bucket(bucket_name=bucket_name)
            return True

        except Exception as exc:
            logger.error(f"Failed to create a bucket: {str(exc)}")
            raise S3OperationException(f"Failed to create a bucket: {str(exc)}")

    async def upload_file_and_get_preassigned_url(self, bucket_name: str, file: UploadFile) -> str:
        """
        Uploads a file to the specified bucket and generates a URL to access the file.

            Params:
                bucket_name (str): The name of the bucket.
                file (UploadFile): The file to upload.

            Returns:
                str: The URL to access the uploaded file.
        """
        try:
            await self.minio_s3_repository.upload_file(bucket_name=bucket_name, file=file)
            file_url = f"{settings.MINIO_URL_TO_OPEN_FILE}/{bucket_name}/{file.filename}"

            return file_url

        except HTTPException as exc:
            logger.error(str(exc))
            raise exc
        except Exception as exc:
            logger.error(f"Failed to upload a file: {str(exc)}")
            raise S3OperationException(f"Failed to upload a file: {str(exc)}")

    async def delete_file(self, bucket_name: str, filename: str) -> bool:
        """
        Deletes file from the specified bucket.

            Params:
                bucket_name (str): The name of the bucket.
                filename (str): The filename of the file to delete.

            Returns:
                bool: True if file is deleted successfully.
        """
        try:
            await self.minio_s3_repository.delete_file(bucket_name=bucket_name, filename=filename)
            return True

        except Exception as exc:
            logger.error(f"Failed to delete file: {str(exc)}")
            raise S3OperationException(f"Failed to delete file: {str(exc)}")
