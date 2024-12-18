from unittest.mock import AsyncMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from exception_handlers.genre_exc_handlers import GenreAlreadyExists, GenreDoesNotExist
from models import Genre
from schemas.genre_schemas import (
    GenreCreateSchema,
    GenreDeleteSchema,
    GenreListQueryParams,
    GenreReadSchema,
    GenresListSchema,
    GenreUpdateSchema,
)
from usecases.genre_usecases import GenreUseCase


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_new_genre():
    new_genre = GenreCreateSchema(name="Фантастика")

    mock_genre_repo = AsyncMock()
    mock_genre_repo.get_genre_by_name.return_value = None
    mock_genre_repo.create_new_genre.return_value = Genre(id=1, **new_genre.model_dump())

    genre_use_case = GenreUseCase(genre_repository=mock_genre_repo)

    result = await genre_use_case.create_new_genre(new_genre=new_genre)

    assert result.id == 1
    assert result.name == new_genre.name

    mock_genre_repo.get_genre_by_name.assert_awaited_once()
    mock_genre_repo.create_new_genre.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_new_genre_name_exists():
    new_genre = GenreCreateSchema(name="Фантастика")

    mock_genre_repo = AsyncMock()
    mock_genre_repo.get_genre_by_name.return_value = Genre(id=1, **new_genre.model_dump())

    genre_use_case = GenreUseCase(genre_repository=mock_genre_repo)

    with pytest.raises(GenreAlreadyExists):
        await genre_use_case.create_new_genre(new_genre=new_genre)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_genre_by_id():
    genre_id = 1

    mock_genre_repo = AsyncMock()
    mock_genre_repo.get_genre_by_id.return_value = Genre(id=1, name="Фантастика")

    genre_use_case = GenreUseCase(genre_repository=mock_genre_repo)

    result = await genre_use_case.get_genre_by_id(genre_id=genre_id)

    assert result.id == 1
    assert result.name == "Фантастика"

    mock_genre_repo.get_genre_by_id.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_genre_by_id_does_not_exist():
    genre_id = 5

    mock_genre_repo = AsyncMock()
    mock_genre_repo.get_genre_by_id.return_value = None

    genre_use_case = GenreUseCase(genre_repository=mock_genre_repo)

    with pytest.raises(GenreDoesNotExist):
        await genre_use_case.get_genre_by_id(genre_id=genre_id)

    mock_genre_repo.get_genre_by_id.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_genre_by_name():
    genre_name = "Фантастика"

    mock_genre_repo = AsyncMock()
    mock_genre_repo.get_genre_by_name.return_value = Genre(id=1, name="Фантастика")

    genre_use_case = GenreUseCase(genre_repository=mock_genre_repo)

    result = await genre_use_case.get_genre_by_name(name=genre_name)

    assert result.id == 1
    assert result.name == "Фантастика"

    mock_genre_repo.get_genre_by_name.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_genre_by_name_db_error():
    genre_name = "Фантастика"

    mock_genre_repo = AsyncMock()
    mock_genre_repo.get_genre_by_name.side_effect = SQLAlchemyError("DB Error")

    genre_use_case = GenreUseCase(genre_repository=mock_genre_repo)

    with pytest.raises(SQLAlchemyError):
        await genre_use_case.get_genre_by_name(name=genre_name)

    mock_genre_repo.get_genre_by_name.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_all_genres():
    request_payload = GenreListQueryParams()
    genre_1 = {"id": 1, "name": "Фантастика"}
    genre_2 = {"id": 2, "name": "Ужасы"}

    mock_genre_repo = AsyncMock()
    mock_genre_repo.get_all_genres.return_value = GenresListSchema(
        genres=[GenreReadSchema(**genre_1), GenreReadSchema(**genre_2)]
    )

    genre_use_case = GenreUseCase(genre_repository=mock_genre_repo)

    result = await genre_use_case.get_all_genres(request_payload=request_payload)

    assert len(result.genres) == 2

    mock_genre_repo.get_all_genres.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_all_genres_bd_error():
    request_payload = GenreListQueryParams()
    genre_1 = {"id": 1, "name": "Фантастика"}
    genre_2 = {"id": 2, "name": "Ужасы"}

    mock_genre_repo = AsyncMock()
    mock_genre_repo.get_all_genres.side_effect = SQLAlchemyError("DB Error")

    genre_use_case = GenreUseCase(genre_repository=mock_genre_repo)

    with pytest.raises(SQLAlchemyError):
        await genre_use_case.get_all_genres(request_payload=request_payload)

    mock_genre_repo.get_all_genres.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_genre():
    genre_id = 1
    updated_data = GenreUpdateSchema(name="Ужасы")
    genre_to_update = {"id": genre_id, "name": "Ужасы"}

    mock_genre_repo = AsyncMock()
    mock_genre_repo.update_genre.return_value = GenreReadSchema(**genre_to_update)

    genre_use_case = GenreUseCase(genre_repository=mock_genre_repo)

    result = await genre_use_case.update_genre(genre_id=genre_id, updated_data=updated_data)

    assert result.name == updated_data.name

    mock_genre_repo.update_genre.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_genre_db_error():
    genre_id = 1
    updated_data = GenreUpdateSchema(name="Ужасы")

    mock_genre_repo = AsyncMock()
    mock_genre_repo.update_genre.side_effect = SQLAlchemyError("DB Error")

    genre_use_case = GenreUseCase(genre_repository=mock_genre_repo)

    with pytest.raises(SQLAlchemyError):
        await genre_use_case.update_genre(genre_id=genre_id, updated_data=updated_data)

    mock_genre_repo.update_genre.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_genre():
    genre_id = 1
    genre_to_delete = Genre(id=genre_id, name="Ужасы")

    mock_genre_repo = AsyncMock()
    mock_genre_repo.delete_genre.return_value = GenreDeleteSchema(
        message=f"Genre '{genre_to_delete.name}' deleted successfully"
    )

    genre_use_case = GenreUseCase(genre_repository=mock_genre_repo)

    result = await genre_use_case.delete_genre(genre_id=genre_id)

    assert result.message == f"Genre '{genre_to_delete.name}' deleted successfully"

    mock_genre_repo.delete_genre.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_genre_db_error():
    genre_id = 1

    mock_genre_repo = AsyncMock()
    mock_genre_repo.delete_genre.side_effect = SQLAlchemyError("DB Error")

    genre_use_case = GenreUseCase(genre_repository=mock_genre_repo)

    with pytest.raises(SQLAlchemyError):
        await genre_use_case.delete_genre(genre_id=genre_id)

    mock_genre_repo.delete_genre.assert_awaited_once()
