from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from exception_handlers.author_exc_handlers import (
    AuthorAlreadyExists,
    AuthorDoesNotExist,
)
from models import Author
from schemas.author_schemas import (
    AuthorCreateSchema,
    AuthorDeleteSchema,
    AuthorListQueryParams,
    AuthorReadSchema,
    AuthorsListSchema,
    AuthorUpdateSchema,
)
from usecases.author_usecases import AuthorUseCase


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_new_author(unit_test_user, unit_test_author, unit_mock_file, unit_mock_minio_usecase):
    new_author = AuthorCreateSchema(**unit_test_author)

    mock_author_repo = AsyncMock()
    mock_author_repo.get_author_by_surname_and_name.return_value = None
    mock_author_repo.create_new_author.return_value = Author(id=1, **new_author.model_dump())

    author_use_case = AuthorUseCase(
        author_repository=mock_author_repo, minio_s3_usecase=unit_mock_minio_usecase
    )

    result = await author_use_case.create_new_author(
        new_author=new_author, file=unit_mock_file, username=unit_test_user["username"]
    )

    assert result.id == 1
    assert result.surname == new_author.surname

    mock_author_repo.get_author_by_surname_and_name.assert_awaited_once()
    mock_author_repo.create_new_author.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_new_author_exists(
    unit_test_user, unit_test_author, unit_mock_file, unit_mock_minio_usecase
):
    new_author = AuthorCreateSchema(**unit_test_author)

    mock_author_repo = AsyncMock()
    mock_author_repo.get_author_by_surname_and_name.return_value = Author(id=1, **new_author.model_dump())

    author_use_case = AuthorUseCase(
        author_repository=mock_author_repo, minio_s3_usecase=unit_mock_minio_usecase
    )

    with pytest.raises(AuthorAlreadyExists):
        await author_use_case.create_new_author(
            new_author=new_author, file=unit_mock_file, username=unit_test_user["username"]
        )

    mock_author_repo.get_author_by_surname_and_name.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_author_by_id(unit_test_author_in_db, unit_mock_minio_usecase):
    author_id = 1

    mock_author_repo = AsyncMock()
    mock_author_repo.get_author_by_id.return_value = Author(**unit_test_author_in_db)

    author_use_case = AuthorUseCase(
        author_repository=mock_author_repo, minio_s3_usecase=unit_mock_minio_usecase
    )

    result = await author_use_case.get_author_by_id(author_id=author_id)

    assert result.id == 1
    assert result.surname == unit_test_author_in_db["surname"]
    assert result.photo_s3_url == unit_test_author_in_db["photo_s3_url"]

    mock_author_repo.get_author_by_id.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_author_by_id_does_not_exist(unit_mock_minio_usecase):
    author_id = 1

    mock_author_repo = AsyncMock()
    mock_author_repo.get_author_by_id.return_value = None

    author_use_case = AuthorUseCase(
        author_repository=mock_author_repo, minio_s3_usecase=unit_mock_minio_usecase
    )

    with pytest.raises(AuthorDoesNotExist):
        await author_use_case.get_author_by_id(author_id=author_id)

    mock_author_repo.get_author_by_id.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_author_by_surname_and_name(unit_test_author_in_db, unit_mock_minio_usecase):
    mock_author_repo = AsyncMock()
    mock_author_repo.get_author_by_surname_and_name.return_value = Author(**unit_test_author_in_db)

    author_use_case = AuthorUseCase(
        author_repository=mock_author_repo, minio_s3_usecase=unit_mock_minio_usecase
    )

    result = await author_use_case.get_author_by_surname_and_name(
        surname=unit_test_author_in_db["surname"], name=unit_test_author_in_db["name"]
    )

    assert result.id == 1
    assert result.surname == unit_test_author_in_db["surname"]
    assert result.name == unit_test_author_in_db["name"]

    mock_author_repo.get_author_by_surname_and_name.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_author_by_surname_and_name_db_error(unit_test_author_in_db, unit_mock_minio_usecase):
    mock_author_repo = AsyncMock()
    mock_author_repo.get_author_by_surname_and_name.side_effect = SQLAlchemyError("DB Error")

    author_use_case = AuthorUseCase(
        author_repository=mock_author_repo, minio_s3_usecase=unit_mock_minio_usecase
    )

    with pytest.raises(SQLAlchemyError):
        await author_use_case.get_author_by_surname_and_name(
            surname=unit_test_author_in_db["surname"], name=unit_test_author_in_db["name"]
        )

    mock_author_repo.get_author_by_surname_and_name.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_all_authors(unit_test_author_in_db, unit_mock_minio_usecase):
    request_payload = AuthorListQueryParams()

    mock_author_repo = AsyncMock()
    mock_author_repo.get_all_authors.return_value = AuthorsListSchema(
        authors=[AuthorReadSchema(**unit_test_author_in_db)]
    )

    author_use_case = AuthorUseCase(
        author_repository=mock_author_repo, minio_s3_usecase=unit_mock_minio_usecase
    )

    result = await author_use_case.get_all_authors(request_payload=request_payload)

    assert len(result.authors) == 1

    mock_author_repo.get_all_authors.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_all_authors_db_error(unit_mock_minio_usecase):
    request_payload = AuthorListQueryParams()

    mock_author_repo = AsyncMock()
    mock_author_repo.get_all_authors.side_effect = SQLAlchemyError("DB Error")

    author_use_case = AuthorUseCase(
        author_repository=mock_author_repo, minio_s3_usecase=unit_mock_minio_usecase
    )

    with pytest.raises(SQLAlchemyError):
        await author_use_case.get_all_authors(request_payload=request_payload)

    mock_author_repo.get_all_authors.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_author(unit_test_user, unit_test_author_in_db, unit_mock_minio_usecase):
    author_id = 1
    updated_data = AuthorUpdateSchema(name="Лев", surname="Толстой", nationality="Россия")

    author_to_update = unit_test_author_in_db
    author_to_update["name"] = updated_data.name
    author_to_update["surname"] = updated_data.surname
    author_to_update["nationality"] = updated_data.nationality
    author_to_update["updated_at"] = datetime.now()
    author_to_update["updated_by"] = unit_test_user["username"]

    mock_author_repo = AsyncMock()
    mock_author_repo.get_author_by_id.return_value = Author(**unit_test_author_in_db)
    mock_author_repo.update_author.return_value = AuthorReadSchema(**author_to_update)

    unit_mock_minio_usecase.ensure_bucket_exists.return_value = True

    author_use_case = AuthorUseCase(
        author_repository=mock_author_repo, minio_s3_usecase=unit_mock_minio_usecase
    )

    result = await author_use_case.update_author(
        author_id=author_id, updated_data=updated_data, file=None, username=unit_test_user["username"]
    )

    assert result.name == updated_data.name
    assert result.surname == updated_data.surname
    assert result.nationality == updated_data.nationality

    mock_author_repo.get_author_by_id.assert_awaited_once()
    mock_author_repo.update_author.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_author_db_error(unit_test_user, unit_test_author_in_db, unit_mock_minio_usecase):
    author_id = 1
    updated_data = AuthorUpdateSchema(name="Лев", surname="Толстой", nationality="Россия")

    mock_author_repo = AsyncMock()
    mock_author_repo.get_author_by_id.return_value = Author(**unit_test_author_in_db)
    mock_author_repo.update_author.side_effect = SQLAlchemyError("DB Error")

    author_use_case = AuthorUseCase(
        author_repository=mock_author_repo, minio_s3_usecase=unit_mock_minio_usecase
    )

    with pytest.raises(SQLAlchemyError):
        await author_use_case.update_author(
            author_id=author_id, updated_data=updated_data, file=None, username=unit_test_user["username"]
        )

    mock_author_repo.get_author_by_id.assert_awaited_once()
    mock_author_repo.update_author.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_author(unit_test_author_in_db, unit_mock_minio_usecase):
    author_id = 1

    mock_author_repo = AsyncMock()
    mock_author_repo.get_author_by_id.return_value = Author(**unit_test_author_in_db)
    mock_author_repo.delete_author.return_value = AuthorDeleteSchema(
        message=f"Author '{unit_test_author_in_db["name"]} {unit_test_author_in_db["surname"]}' deleted successfully"
    )

    unit_mock_minio_usecase.ensure_bucket_exists.return_value = True

    author_use_case = AuthorUseCase(
        author_repository=mock_author_repo, minio_s3_usecase=unit_mock_minio_usecase
    )

    result = await author_use_case.delete_author(author_id=author_id)

    assert (
        result.message
        == f"Author '{unit_test_author_in_db["name"]} {unit_test_author_in_db["surname"]}' deleted successfully"
    )

    mock_author_repo.get_author_by_id.assert_awaited_once()
    mock_author_repo.delete_author.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_author_db_error(unit_test_author_in_db, unit_mock_minio_usecase):
    author_id = 1

    mock_author_repo = AsyncMock()
    mock_author_repo.get_author_by_id.return_value = Author(**unit_test_author_in_db)
    mock_author_repo.delete_author.side_effect = SQLAlchemyError("DB Error")

    unit_mock_minio_usecase.ensure_bucket_exists.return_value = True

    author_use_case = AuthorUseCase(
        author_repository=mock_author_repo, minio_s3_usecase=unit_mock_minio_usecase
    )

    with pytest.raises(SQLAlchemyError):
        await author_use_case.delete_author(author_id=author_id)

    mock_author_repo.get_author_by_id.assert_awaited_once()
    mock_author_repo.delete_author.assert_awaited_once()
