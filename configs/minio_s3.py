from botocore.config import Config

from configs.settings import settings

minio_config = Config(region_name=settings.MINIO_REGION, signature_version="v4")

minio_bucket_name = settings.MINIO_BUCKET_NAME