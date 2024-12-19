from fastapi import Depends, UploadFile

from dependencies.minio_s3_dependency import get_minio_s3_usecase
from repositories.author_repository import AuthorRepository
from schemas.author_schemas import AuthorCreateSchema
from usecases.minio_s3_usecases import MinioS3UseCase


class AuthorUseCase:
    def __init__(self, author_repository: AuthorRepository):
        self.author_repository = author_repository

    async def create_new_author(
        self,
        new_author: AuthorCreateSchema,
        file: UploadFile,
        username: str,
        minio_s3_usecase: MinioS3UseCase = Depends(get_minio_s3_usecase),
    ):
        pass
