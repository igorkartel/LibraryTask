import aioboto3
from aiobotocore.client import AioBaseClient
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import Depends

from configs.logger import logger
from configs.minio_s3 import minio_config
from configs.settings import settings
from exception_handlers.minio_s3_exc_handlers import S3OperationException
from repositories.minio_s3_repository import MinioS3Repository
from usecases.minio_s3_usecases import MinioS3UseCase

minio_aioboto3_session = aioboto3.session.Session()


async def get_minio_s3_client() -> AioBaseClient:
    try:
        async with minio_aioboto3_session.client(
            service_name="s3",
            endpoint_url=settings.MINIO_URL,
            aws_access_key_id=settings.MINIO_ROOT_USER,
            aws_secret_access_key=settings.MINIO_ROOT_PASSWORD,
            config=minio_config,
        ) as minio_s3_client:
            yield minio_s3_client
    except (ClientError, BotoCoreError) as exc:
        logger.error(f"Failed to get Minio S3 client: {str(exc)}")
        raise S3OperationException(message=f"Failed to get Minio S3 client: {str(exc)}")


async def get_minio_s3_usecase(s3_client: AioBaseClient = Depends(get_minio_s3_client)) -> MinioS3UseCase:
    minio_s3_repository = MinioS3Repository(s3_client)
    return MinioS3UseCase(minio_s3_repository)
