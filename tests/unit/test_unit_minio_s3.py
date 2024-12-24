from unittest.mock import AsyncMock, MagicMock

import pytest
from botocore.exceptions import ClientError

from exception_handlers.minio_s3_exc_handlers import S3OperationException
from usecases.minio_s3_usecases import MinioS3UseCase


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ensure_bucket_exists():
    bucket_name = "Test_bucket"

    mock_minio_repo = AsyncMock()
    mock_minio_repo.ensure_bucket_exists.return_value = None

    minio_use_case = MinioS3UseCase(minio_s3_repository=mock_minio_repo)

    result = await minio_use_case.ensure_bucket_exists(bucket_name=bucket_name)

    assert result is True

    mock_minio_repo.ensure_bucket_exists.assert_called_once_with(bucket_name=bucket_name)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_ensure_bucket_exists_not_found():
    bucket_name = "Test_bucket"

    mock_minio_repo = AsyncMock()
    mock_minio_repo.ensure_bucket_exists.side_effect = ClientError({"Error": {"Code": "404"}}, "HeadBucket")

    minio_use_case = MinioS3UseCase(minio_s3_repository=mock_minio_repo)

    result = await minio_use_case.ensure_bucket_exists(bucket_name=bucket_name)

    assert result is False

    mock_minio_repo.ensure_bucket_exists.assert_called_once_with(bucket_name=bucket_name)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_bucket():
    bucket_name = "Test_bucket"

    mock_minio_repo = AsyncMock()
    mock_minio_repo.create_bucket.return_value = None

    minio_use_case = MinioS3UseCase(minio_s3_repository=mock_minio_repo)

    result = await minio_use_case.create_bucket(bucket_name=bucket_name)

    assert result is True

    mock_minio_repo.create_bucket.assert_called_once_with(bucket_name=bucket_name)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_bucket_exception():
    bucket_name = "Test_bucket"

    mock_minio_repo = AsyncMock()
    mock_minio_repo.create_bucket.side_effect = Exception("Unexpected error")

    minio_use_case = MinioS3UseCase(minio_s3_repository=mock_minio_repo)

    with pytest.raises(S3OperationException, match="Failed to create a bucket"):
        await minio_use_case.create_bucket(bucket_name=bucket_name)

    mock_minio_repo.create_bucket.assert_called_once_with(bucket_name=bucket_name)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_upload_file_and_get_presigned_url():
    bucket_name = "Test_bucket"
    file = MagicMock()
    file.filename = "test.jpg"

    mock_minio_repo = AsyncMock()
    mock_minio_repo.upload_file.return_value = None

    minio_use_case = MinioS3UseCase(minio_s3_repository=mock_minio_repo)

    result = await minio_use_case.upload_file_and_get_presigned_url(bucket_name=bucket_name, file=file)

    assert result == "http://localhost:9000/Test_bucket/test.jpg"

    mock_minio_repo.upload_file.assert_called_once_with(bucket_name=bucket_name, file=file)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_upload_file_and_get_presigned_url_exception():
    bucket_name = "Test_bucket"
    file = MagicMock()
    file.filename = "test.jpg"

    mock_minio_repo = AsyncMock()
    mock_minio_repo.upload_file.side_effect = Exception("Unexpected error")

    minio_use_case = MinioS3UseCase(minio_s3_repository=mock_minio_repo)

    with pytest.raises(S3OperationException, match="Failed to upload a file"):
        await minio_use_case.upload_file_and_get_presigned_url(bucket_name=bucket_name, file=file)

    mock_minio_repo.upload_file.assert_called_once_with(bucket_name=bucket_name, file=file)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_file():
    bucket_name = "Test_bucket"
    filename = "test.jpg"

    mock_minio_repo = AsyncMock()
    mock_minio_repo.delete_file.return_value = None

    minio_use_case = MinioS3UseCase(minio_s3_repository=mock_minio_repo)

    result = await minio_use_case.delete_file(bucket_name=bucket_name, filename=filename)

    assert result is True

    mock_minio_repo.delete_file.assert_called_once_with(bucket_name=bucket_name, filename=filename)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_file_exception():
    bucket_name = "Test_bucket"
    filename = "test.jpg"

    mock_minio_repo = AsyncMock()
    mock_minio_repo.delete_file.side_effect = Exception("Unexpected error")

    minio_use_case = MinioS3UseCase(minio_s3_repository=mock_minio_repo)

    with pytest.raises(S3OperationException, match="Failed to delete file"):
        await minio_use_case.delete_file(bucket_name=bucket_name, filename=filename)

    mock_minio_repo.delete_file.assert_called_once_with(bucket_name=bucket_name, filename=filename)
