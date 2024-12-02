import aioboto3
from aiobotocore.client import AioBaseClient
from botocore.exceptions import BotoCoreError, ClientError

from configs.minio_s3 import minio_config

# from configs.custom_exceptions import S3OperationException
# from configs.logger import logger
from configs.settings import settings

minio_aioboto3_session = aioboto3.session.Session()


async def get_minio_s3_client() -> AioBaseClient:
    try:
        async with minio_aioboto3_session.client(
            service_name="s3",
            endpoint_url=settings.MINIO_URL,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            config=minio_config,
        ) as minio_s3_client:
            yield minio_s3_client
    except (ClientError, BotoCoreError) as e:
        #     logger.error(f"Failed to get AWS S3 client: {str(e)}")
        #     raise S3OperationException(message=f"Failed to get AWS S3 client: {str(e)}")
        # except Exception as e:
        #     logger.error(str(e))
        raise
