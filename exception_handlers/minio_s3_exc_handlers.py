from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class S3OperationException(Exception):
    def __init__(self, message: str):
        self.detail = message
        super().__init__(self.detail)


class BucketS3DoesNotExist(Exception):
    def __init__(self):
        self.detail = "No such bucket found"
        super().__init__(self.detail)


def register_minio_exception_handlers(app: FastAPI):
    @app.exception_handler(S3OperationException)
    async def minio_s3_exception_handler(request: Request, exc: S3OperationException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.detail},
        )

    @app.exception_handler(BucketS3DoesNotExist)
    async def bucket_s3_does_not_exist_exception_handler(request: Request, exc: BucketS3DoesNotExist):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.detail},
        )
