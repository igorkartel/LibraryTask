from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from exception_handlers.book_exc_handlers import BookDoesNotExist
from models import Book, BookInstance
from schemas.author_schemas import AuthorReadSchema
from schemas.book_schemas import (
    BookInstanceCreateSchema,
    BookInstanceDeleteSchema,
    BookInstanceReadSchema,
    BookInstanceUpdateSchema,
)
from schemas.common_circular_schemas import BookWithInstancesReadSchema
from schemas.genre_schemas import GenreReadSchema
from usecases.book_instance_usecases import BookInstanceUseCase


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_new_book_instance(
    unit_test_user, unit_test_book_in_db, unit_test_book_instance, unit_mock_file, unit_mock_minio_usecase
):
    new_book_instance = BookInstanceCreateSchema(
        book_id=unit_test_book_in_db["id"], **unit_test_book_instance
    )

    mock_book_inst_repo = AsyncMock()
    mock_book_inst_repo.create_new_book_instance.return_value = BookInstance(
        id=1, **new_book_instance.model_dump()
    )

    book_use_case = AsyncMock()
    book_use_case.get_book_by_id.return_value = Book(**unit_test_book_in_db)

    book_inst_use_case = BookInstanceUseCase(
        book_instance_repository=mock_book_inst_repo,
        book_usecase=book_use_case,
        minio_s3_usecase=unit_mock_minio_usecase,
    )

    result = await book_inst_use_case.create_new_book_instance(
        book_id=unit_test_book_in_db["id"],
        new_book_instance=new_book_instance,
        file=unit_mock_file,
        username=unit_test_user["username"],
    )

    assert result.id == 1
    assert result.book_id == unit_test_book_in_db["id"]
    assert result.pages == unit_test_book_instance["pages"]

    book_use_case.get_book_by_id.assert_awaited_once()
    mock_book_inst_repo.create_new_book_instance.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_new_book_instance_db_error(
    unit_test_user, unit_test_book_in_db, unit_test_book_instance, unit_mock_file, unit_mock_minio_usecase
):
    new_book_instance = BookInstanceCreateSchema(
        book_id=unit_test_book_in_db["id"], **unit_test_book_instance
    )

    mock_book_inst_repo = AsyncMock()
    mock_book_inst_repo.create_new_book_instance.side_effect = SQLAlchemyError("DB Error")

    book_use_case = AsyncMock()
    book_use_case.get_book_by_id.return_value = Book(**unit_test_book_in_db)

    book_inst_use_case = BookInstanceUseCase(
        book_instance_repository=mock_book_inst_repo,
        book_usecase=book_use_case,
        minio_s3_usecase=unit_mock_minio_usecase,
    )

    with pytest.raises(SQLAlchemyError):
        await book_inst_use_case.create_new_book_instance(
            book_id=unit_test_book_in_db["id"],
            new_book_instance=new_book_instance,
            file=unit_mock_file,
            username=unit_test_user["username"],
        )

    book_use_case.get_book_by_id.assert_awaited_once()
    mock_book_inst_repo.create_new_book_instance.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_book_instance_by_id(unit_test_book_instance_in_db, unit_mock_minio_usecase):
    book_instance_id = 1

    mock_book_inst_repo = AsyncMock()
    mock_book_inst_repo.get_book_instance_by_id.return_value = BookInstance(**unit_test_book_instance_in_db)

    book_use_case = AsyncMock()

    book_inst_use_case = BookInstanceUseCase(
        book_instance_repository=mock_book_inst_repo,
        book_usecase=book_use_case,
        minio_s3_usecase=unit_mock_minio_usecase,
    )

    result = await book_inst_use_case.get_book_instance_by_id(book_instance_id=book_instance_id)

    assert result.id == book_instance_id
    assert result.book_id == unit_test_book_instance_in_db["book_id"]
    assert result.cover_s3_url == unit_test_book_instance_in_db["cover_s3_url"]

    mock_book_inst_repo.get_book_instance_by_id.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_book_instance_by_id_does_not_exist(unit_mock_minio_usecase):
    book_instance_id = 2

    mock_book_inst_repo = AsyncMock()
    mock_book_inst_repo.get_book_instance_by_id.return_value = None

    book_use_case = AsyncMock()

    book_inst_use_case = BookInstanceUseCase(
        book_instance_repository=mock_book_inst_repo,
        book_usecase=book_use_case,
        minio_s3_usecase=unit_mock_minio_usecase,
    )

    with pytest.raises(BookDoesNotExist):
        await book_inst_use_case.get_book_instance_by_id(book_instance_id=book_instance_id)

    mock_book_inst_repo.get_book_instance_by_id.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_all_instances_by_book_id(
    unit_test_book_in_db, unit_test_book_instance_in_db, unit_test_author_in_db, unit_mock_minio_usecase
):
    mock_book_inst_repo = AsyncMock()
    mock_book_inst_repo.get_all_instances_by_book_id.return_value = BookWithInstancesReadSchema(
        **unit_test_book_in_db,
        authors=[AuthorReadSchema(**unit_test_author_in_db)],
        genres=[GenreReadSchema(id=1, name="Роман")],
        instances=[BookInstanceReadSchema(**unit_test_book_instance_in_db)],
    )

    book_use_case = AsyncMock()

    book_inst_use_case = BookInstanceUseCase(
        book_instance_repository=mock_book_inst_repo,
        book_usecase=book_use_case,
        minio_s3_usecase=unit_mock_minio_usecase,
    )

    result = await book_inst_use_case.get_all_instances_by_book_id(book_id=unit_test_book_in_db["id"])

    assert result.id == unit_test_book_in_db["id"]
    assert len(result.authors) == 1
    assert len(result.genres) == 1
    assert len(result.instances) == 1

    mock_book_inst_repo.get_all_instances_by_book_id.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_all_instances_by_book_id_db_error(unit_test_book_in_db, unit_mock_minio_usecase):
    mock_book_inst_repo = AsyncMock()
    mock_book_inst_repo.get_all_instances_by_book_id.side_effect = SQLAlchemyError("DB Error")

    book_use_case = AsyncMock()

    book_inst_use_case = BookInstanceUseCase(
        book_instance_repository=mock_book_inst_repo,
        book_usecase=book_use_case,
        minio_s3_usecase=unit_mock_minio_usecase,
    )

    with pytest.raises(SQLAlchemyError):
        await book_inst_use_case.get_all_instances_by_book_id(book_id=unit_test_book_in_db["id"])

    mock_book_inst_repo.get_all_instances_by_book_id.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_book_instance(
    unit_test_user,
    unit_test_book_in_db,
    unit_test_book_instance_in_db,
    unit_mock_file,
    unit_mock_minio_usecase,
):
    book_instance_id = 1
    book_item_to_update = BookInstanceUpdateSchema(imprint_year=2015, pages=400)

    book_instance_to_update = unit_test_book_instance_in_db
    book_instance_to_update["imprint_year"] = book_item_to_update.imprint_year
    book_instance_to_update["pages"] = book_item_to_update.pages
    book_instance_to_update["updated_at"] = datetime.now()
    book_instance_to_update["updated_by"] = unit_test_user["username"]

    mock_book_inst_repo = AsyncMock()
    mock_book_inst_repo.get_book_instance_by_id.return_value = BookInstance(**unit_test_book_instance_in_db)
    mock_book_inst_repo.update_book_instance.return_value = BookInstance(**book_instance_to_update)

    book_use_case = AsyncMock()
    book_use_case.get_book_by_id.return_value = Book(**unit_test_book_in_db)

    unit_mock_minio_usecase.ensure_bucket_exists.return_value = True

    book_inst_use_case = BookInstanceUseCase(
        book_instance_repository=mock_book_inst_repo,
        book_usecase=book_use_case,
        minio_s3_usecase=unit_mock_minio_usecase,
    )

    result = await book_inst_use_case.update_book_instance(
        book_instance_id=book_instance_id,
        book_item_to_update=book_item_to_update,
        file=unit_mock_file,
        username=unit_test_user["username"],
    )

    assert result.imprint_year == book_item_to_update.imprint_year
    assert result.pages == book_item_to_update.pages

    mock_book_inst_repo.get_book_instance_by_id.assert_awaited_once()
    book_use_case.get_book_by_id.assert_awaited_once()
    mock_book_inst_repo.update_book_instance.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_book_instance_db_error(
    unit_test_user,
    unit_test_book_in_db,
    unit_test_book_instance_in_db,
    unit_mock_file,
    unit_mock_minio_usecase,
):
    book_instance_id = 1
    book_item_to_update = BookInstanceUpdateSchema(imprint_year=2015, pages=400)

    mock_book_inst_repo = AsyncMock()
    mock_book_inst_repo.get_book_instance_by_id.return_value = BookInstance(**unit_test_book_instance_in_db)
    mock_book_inst_repo.update_book_instance.side_effect = SQLAlchemyError("DB Error")

    book_use_case = AsyncMock()
    book_use_case.get_book_by_id.return_value = Book(**unit_test_book_in_db)

    unit_mock_minio_usecase.ensure_bucket_exists.return_value = True

    book_inst_use_case = BookInstanceUseCase(
        book_instance_repository=mock_book_inst_repo,
        book_usecase=book_use_case,
        minio_s3_usecase=unit_mock_minio_usecase,
    )

    with pytest.raises(SQLAlchemyError):
        await book_inst_use_case.update_book_instance(
            book_instance_id=book_instance_id,
            book_item_to_update=book_item_to_update,
            file=unit_mock_file,
            username=unit_test_user["username"],
        )

    mock_book_inst_repo.get_book_instance_by_id.assert_awaited_once()
    book_use_case.get_book_by_id.assert_awaited_once()
    mock_book_inst_repo.update_book_instance.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_book_instance(
    unit_test_book_in_db, unit_test_book_instance_in_db, unit_mock_minio_usecase
):
    book_instance_id = 1

    mock_book_inst_repo = AsyncMock()
    mock_book_inst_repo.get_book_instance_by_id.return_value = BookInstance(**unit_test_book_instance_in_db)
    mock_book_inst_repo.delete_book_instance.return_value = BookInstanceDeleteSchema(
        message=f"Book item of the book '{unit_test_book_in_db["title_rus"]}' deleted successfully"
    )

    book_use_case = AsyncMock()
    book_use_case.get_book_by_id.return_value = Book(**unit_test_book_in_db)

    unit_mock_minio_usecase.ensure_bucket_exists.return_value = True

    book_inst_use_case = BookInstanceUseCase(
        book_instance_repository=mock_book_inst_repo,
        book_usecase=book_use_case,
        minio_s3_usecase=unit_mock_minio_usecase,
    )

    result = await book_inst_use_case.delete_book_instance(book_instance_id=book_instance_id)

    assert (
        result.message == f"Book item of the book '{unit_test_book_in_db["title_rus"]}' deleted successfully"
    )

    mock_book_inst_repo.get_book_instance_by_id.assert_awaited_once()
    book_use_case.get_book_by_id.assert_awaited_once()
    mock_book_inst_repo.delete_book_instance.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_book_instance_db_error(
    unit_test_book_in_db, unit_test_book_instance_in_db, unit_mock_minio_usecase
):
    book_instance_id = 1

    mock_book_inst_repo = AsyncMock()
    mock_book_inst_repo.get_book_instance_by_id.return_value = BookInstance(**unit_test_book_instance_in_db)
    mock_book_inst_repo.delete_book_instance.side_effect = SQLAlchemyError("DB Error")

    book_use_case = AsyncMock()
    book_use_case.get_book_by_id.return_value = Book(**unit_test_book_in_db)

    unit_mock_minio_usecase.ensure_bucket_exists.return_value = True

    book_inst_use_case = BookInstanceUseCase(
        book_instance_repository=mock_book_inst_repo,
        book_usecase=book_use_case,
        minio_s3_usecase=unit_mock_minio_usecase,
    )

    with pytest.raises(SQLAlchemyError):
        await book_inst_use_case.delete_book_instance(book_instance_id=book_instance_id)

    mock_book_inst_repo.get_book_instance_by_id.assert_awaited_once()
    book_use_case.get_book_by_id.assert_awaited_once()
    mock_book_inst_repo.delete_book_instance.assert_awaited_once()
