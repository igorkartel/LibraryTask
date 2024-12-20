from io import BytesIO

from fastapi import HTTPException, UploadFile
from PIL import Image
from starlette import status

from configs.settings import settings
from repositories.abstract_repositories import AbstractMinioS3Repository


class MinioS3Repository(AbstractMinioS3Repository):
    async def ensure_bucket_exists(self, bucket_name: str) -> None:
        await self.s3_client.head_bucket(Bucket=bucket_name)

    async def create_bucket(self, bucket_name: str) -> None:
        await self.s3_client.create_bucket(
            Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": settings.MINIO_REGION}
        )

    async def upload_file(self, bucket_name: str, file: UploadFile) -> None:
        # Checking file's MIME-type
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="File must be in JPEG or PNG format"
            )

        try:
            image = Image.open(file.file)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file")

        # Checking image format
        if image.format not in ["JPEG", "PNG"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="File must be in JPEG or PNG format"
            )

        # Checking and changing image size if needed
        if image.width > 200 or image.height > 300:
            image.thumbnail((200, 300))

        # Saving image into memory
        buffer = BytesIO()
        image.save(buffer, format=image.format)
        buffer.seek(0)

        await self.s3_client.upload_fileobj(buffer, bucket_name, file.filename)

    async def delete_file(self, bucket_name: str, filename: str) -> None:
        await self.s3_client.delete_object(Bucket=bucket_name, Key=filename)
