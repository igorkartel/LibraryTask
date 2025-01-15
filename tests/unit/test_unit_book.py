from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from exception_handlers.book_exc_handlers import BookDoesNotExist
from models import Author, Book, Genre
from schemas.author_schemas import AuthorReadSchema
from schemas.book_schemas import (
    BookCreateSchema,
    BookDeleteSchema,
    BookListQueryParams,
    BookReadSchema,
    BookUpdateSchema,
    BookWithAuthorsGenresCreateSchema,
)
from schemas.common_circular_schemas import (
    BookListSchema,
    BookWithAuthorsGenresReadSchema,
    BookWithAuthorsReadSchema,
)
from schemas.genre_schemas import GenreReadSchema
from usecases.book_usecases import BookUseCase


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_new_book(unit_test_user, unit_test_book):
    new_book = BookCreateSchema(**unit_test_book)

    mock_book_repo = AsyncMock()
    mock_book_repo.create_new_book.return_value = Book(id=1, **new_book.model_dump())

    author_use_case = AsyncMock()
    genre_use_case = AsyncMock()
    book_use_case = BookUseCase(
        book_repository=mock_book_repo, author_usecase=author_use_case, genre_usecase=genre_use_case
    )

    result = await book_use_case.create_new_book(new_book=new_book, username=unit_test_user["username"])

    assert result.id == 1
    assert result.title_rus == new_book.title_rus

    mock_book_repo.create_new_book.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_new_book_db_error(unit_test_user, unit_test_book):
    new_book = BookCreateSchema(**unit_test_book)

    mock_book_repo = AsyncMock()
    mock_book_repo.create_new_book.side_effect = SQLAlchemyError("DB Error")

    author_use_case = AsyncMock()
    genre_use_case = AsyncMock()
    book_use_case = BookUseCase(
        book_repository=mock_book_repo, author_usecase=author_use_case, genre_usecase=genre_use_case
    )

    with pytest.raises(SQLAlchemyError):
        await book_use_case.create_new_book(new_book=new_book, username=unit_test_user["username"])

    mock_book_repo.create_new_book.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_map_book_to_existing_authors(unit_test_user, unit_test_book_in_db, unit_test_author_in_db):
    book_id = 1
    author_ids = [1]
    updated_book = BookWithAuthorsReadSchema(
        **unit_test_book_in_db, authors=[AuthorReadSchema(**unit_test_author_in_db)]
    )
    updated_book.updated_by = unit_test_user["username"]

    mock_book_repo = AsyncMock()
    mock_book_repo.get_book_by_id.return_value = Book(**unit_test_book_in_db)
    mock_book_repo.update_book.return_value = updated_book

    author_use_case = AsyncMock()
    author_use_case.get_author_by_id.return_value = Author(**unit_test_author_in_db)
    genre_use_case = AsyncMock()
    book_use_case = BookUseCase(
        book_repository=mock_book_repo, author_usecase=author_use_case, genre_usecase=genre_use_case
    )

    result = await book_use_case.map_book_to_existing_authors(
        book_id=book_id, author_ids=author_ids, username=unit_test_user["username"]
    )

    assert result.title_rus == unit_test_book_in_db["title_rus"]
    assert result.updated_by == unit_test_user["username"]
    assert len(result.authors) == 1

    mock_book_repo.get_book_by_id.assert_awaited_once()
    author_use_case.get_author_by_id.assert_awaited_once()
    mock_book_repo.update_book.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_map_book_to_existing_authors_db_error(
    unit_test_user, unit_test_book_in_db, unit_test_author_in_db
):
    book_id = 1
    author_ids = [1]

    mock_book_repo = AsyncMock()
    mock_book_repo.get_book_by_id.return_value = Book(**unit_test_book_in_db)
    mock_book_repo.update_book.side_effect = SQLAlchemyError("DB Error")

    author_use_case = AsyncMock()
    author_use_case.get_author_by_id.return_value = Author(**unit_test_author_in_db)
    genre_use_case = AsyncMock()
    book_use_case = BookUseCase(
        book_repository=mock_book_repo, author_usecase=author_use_case, genre_usecase=genre_use_case
    )

    with pytest.raises(SQLAlchemyError):
        await book_use_case.map_book_to_existing_authors(
            book_id=book_id, author_ids=author_ids, username=unit_test_user["username"]
        )

    mock_book_repo.get_book_by_id.assert_awaited_once()
    author_use_case.get_author_by_id.assert_awaited_once()
    mock_book_repo.update_book.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_map_book_to_existing_genres(unit_test_user, unit_test_book_in_db, unit_test_author_in_db):
    book_id = 1
    genre_ids = [1]
    updated_book = BookWithAuthorsGenresReadSchema(
        **unit_test_book_in_db,
        authors=[AuthorReadSchema(**unit_test_author_in_db)],
        genres=[GenreReadSchema(id=1, name="Роман")],
    )
    updated_book.updated_by = unit_test_user["username"]

    mock_book_repo = AsyncMock()
    mock_book_repo.get_book_by_id.return_value = Book(**unit_test_book_in_db)
    mock_book_repo.update_book.return_value = updated_book

    author_use_case = AsyncMock()
    genre_use_case = AsyncMock()
    genre_use_case.get_genre_by_id.return_value = Genre(id=1, name="Роман")
    book_use_case = BookUseCase(
        book_repository=mock_book_repo, author_usecase=author_use_case, genre_usecase=genre_use_case
    )

    result = await book_use_case.map_book_to_existing_genres(
        book_id=book_id, genre_ids=genre_ids, username=unit_test_user["username"]
    )

    assert result.title_rus == unit_test_book_in_db["title_rus"]
    assert result.updated_by == unit_test_user["username"]
    assert len(result.genres) == 1

    mock_book_repo.get_book_by_id.assert_awaited_once()
    genre_use_case.get_genre_by_id.assert_awaited_once()
    mock_book_repo.update_book.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_map_book_to_existing_genres_db_error(
    unit_test_user, unit_test_book_in_db, unit_test_author_in_db
):
    book_id = 1
    genre_ids = [1]

    mock_book_repo = AsyncMock()
    mock_book_repo.get_book_by_id.return_value = Book(**unit_test_book_in_db)
    mock_book_repo.update_book.side_effect = SQLAlchemyError("DB Error")

    author_use_case = AsyncMock()
    genre_use_case = AsyncMock()
    genre_use_case.get_genre_by_id.return_value = Genre(id=1, name="Роман")
    book_use_case = BookUseCase(
        book_repository=mock_book_repo, author_usecase=author_use_case, genre_usecase=genre_use_case
    )

    with pytest.raises(SQLAlchemyError):
        await book_use_case.map_book_to_existing_genres(
            book_id=book_id, genre_ids=genre_ids, username=unit_test_user["username"]
        )

    mock_book_repo.get_book_by_id.assert_awaited_once()
    genre_use_case.get_genre_by_id.assert_awaited_once()
    mock_book_repo.update_book.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_new_book_with_author_and_genre(
    unit_test_author_in_db,
    unit_test_book_in_db,
    unit_test_book_with_author_and_genre,
    unit_mock_file,
):
    new_book = BookWithAuthorsGenresCreateSchema(**unit_test_book_with_author_and_genre)

    mock_book_repo = AsyncMock()
    mock_book_repo.get_book_by_title_and_author.return_value = None
    mock_book_repo.create_new_book.return_value = Book(
        **unit_test_book_in_db,
        authors=[Author(**unit_test_author_in_db)],
        genres=[Genre(id=1, name="Роман")],
    )

    author_use_case = AsyncMock()
    author_use_case.get_author_by_surname_and_name.return_value = None
    author_use_case.create_new_author.return_value = Author(**unit_test_author_in_db)
    genre_use_case = AsyncMock()
    genre_use_case.get_genre_by_name.return_value = None
    genre_use_case.create_new_genre.return_value = Genre(
        id=1, name=unit_test_book_with_author_and_genre["genre_name"]
    )
    book_use_case = BookUseCase(
        book_repository=mock_book_repo, author_usecase=author_use_case, genre_usecase=genre_use_case
    )

    result = await book_use_case.create_new_book_with_author_and_genre(
        new_book=new_book, file=unit_mock_file, username="librarian"
    )

    assert result.id == 1
    assert result.title_rus == new_book.title_rus
    assert result.authors[0].surname == unit_test_author_in_db["surname"]
    assert result.genres[0].name == "Роман"

    author_use_case.get_author_by_surname_and_name.assert_awaited_once()
    author_use_case.create_new_author.assert_awaited_once()
    genre_use_case.get_genre_by_name.assert_awaited_once()
    genre_use_case.create_new_genre.assert_awaited_once()
    mock_book_repo.get_book_by_title_and_author.assert_awaited_once()
    mock_book_repo.create_new_book.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_new_book_with_author_and_genre_db_error(
    unit_test_book_with_author_and_genre,
    unit_mock_file,
):
    new_book = BookWithAuthorsGenresCreateSchema(**unit_test_book_with_author_and_genre)

    mock_book_repo = AsyncMock()

    author_use_case = AsyncMock()
    author_use_case.get_author_by_surname_and_name.return_value = None
    author_use_case.create_new_author.side_effect = SQLAlchemyError("DB Error")
    genre_use_case = AsyncMock()
    book_use_case = BookUseCase(
        book_repository=mock_book_repo, author_usecase=author_use_case, genre_usecase=genre_use_case
    )

    with pytest.raises(SQLAlchemyError):
        await book_use_case.create_new_book_with_author_and_genre(
            new_book=new_book, file=unit_mock_file, username="librarian"
        )

    author_use_case.get_author_by_surname_and_name.assert_awaited_once()
    author_use_case.create_new_author.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_book_by_id(unit_test_book_in_db):
    book_id = 1

    mock_book_repo = AsyncMock()
    mock_book_repo.get_book_by_id.return_value = Book(**unit_test_book_in_db)

    author_use_case = AsyncMock()
    genre_use_case = AsyncMock()
    book_use_case = BookUseCase(
        book_repository=mock_book_repo, author_usecase=author_use_case, genre_usecase=genre_use_case
    )

    result = await book_use_case.get_book_by_id(book_id=book_id)

    assert result.id == book_id
    assert result.title_rus == unit_test_book_in_db["title_rus"]

    mock_book_repo.get_book_by_id.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_book_by_id_does_not_exist():
    book_id = 1

    mock_book_repo = AsyncMock()
    mock_book_repo.get_book_by_id.return_value = None

    author_use_case = AsyncMock()
    genre_use_case = AsyncMock()
    book_use_case = BookUseCase(
        book_repository=mock_book_repo, author_usecase=author_use_case, genre_usecase=genre_use_case
    )

    with pytest.raises(BookDoesNotExist):
        await book_use_case.get_book_by_id(book_id=book_id)

    mock_book_repo.get_book_by_id.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_books_by_title(unit_test_book_in_db, unit_test_author_in_db):
    book_title = "Книга"

    mock_book_repo = AsyncMock()
    mock_book_repo.get_books_by_title.return_value = BookListSchema(
        books=[
            BookWithAuthorsReadSchema(
                **unit_test_book_in_db, authors=[AuthorReadSchema(**unit_test_author_in_db)]
            )
        ]
    )

    author_use_case = AsyncMock()
    genre_use_case = AsyncMock()
    book_use_case = BookUseCase(
        book_repository=mock_book_repo, author_usecase=author_use_case, genre_usecase=genre_use_case
    )

    result = await book_use_case.get_books_by_title(book_title=book_title)

    assert result.books[0].id == unit_test_book_in_db["id"]
    assert result.books[0].title_rus == book_title
    assert result.books[0].authors[0].surname == unit_test_author_in_db["surname"]

    mock_book_repo.get_books_by_title.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_books_by_title_does_not_exist():
    book_title = "Книга"

    mock_book_repo = AsyncMock()
    mock_book_repo.get_books_by_title.side_effect = BookDoesNotExist(message="No books found")

    author_use_case = AsyncMock()
    genre_use_case = AsyncMock()
    book_use_case = BookUseCase(
        book_repository=mock_book_repo, author_usecase=author_use_case, genre_usecase=genre_use_case
    )

    with pytest.raises(BookDoesNotExist):
        await book_use_case.get_books_by_title(book_title=book_title)

    mock_book_repo.get_books_by_title.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_book_by_title_and_author(unit_test_book_in_db, unit_test_author_in_db):
    title = "Книга"
    author = "Кинг"

    mock_book_repo = AsyncMock()
    mock_book_repo.get_book_by_title_and_author.return_value = BookWithAuthorsReadSchema(
        **unit_test_book_in_db, authors=[AuthorReadSchema(**unit_test_author_in_db)]
    )

    author_use_case = AsyncMock()
    genre_use_case = AsyncMock()
    book_use_case = BookUseCase(
        book_repository=mock_book_repo, author_usecase=author_use_case, genre_usecase=genre_use_case
    )

    result = await book_use_case.get_book_by_title_and_author(title=title, author=author)

    assert result.id == unit_test_book_in_db["id"]
    assert result.title_rus == title
    assert result.authors[0].surname == author

    mock_book_repo.get_book_by_title_and_author.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_book_by_title_and_author_db_error():
    title = "Книга"
    author = "Кинг"

    mock_book_repo = AsyncMock()
    mock_book_repo.get_book_by_title_and_author.side_effect = SQLAlchemyError("DB Error")

    author_use_case = AsyncMock()
    genre_use_case = AsyncMock()
    book_use_case = BookUseCase(
        book_repository=mock_book_repo, author_usecase=author_use_case, genre_usecase=genre_use_case
    )

    with pytest.raises(SQLAlchemyError):
        await book_use_case.get_book_by_title_and_author(title=title, author=author)

    mock_book_repo.get_book_by_title_and_author.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_all_books(unit_test_book_in_db, unit_test_author_in_db):
    request_payload = BookListQueryParams()

    mock_book_repo = AsyncMock()
    mock_book_repo.get_all_books.return_value = BookListSchema(
        books=[
            BookWithAuthorsReadSchema(
                **unit_test_book_in_db, authors=[AuthorReadSchema(**unit_test_author_in_db)]
            )
        ]
    )

    author_use_case = AsyncMock()
    genre_use_case = AsyncMock()
    book_use_case = BookUseCase(
        book_repository=mock_book_repo, author_usecase=author_use_case, genre_usecase=genre_use_case
    )

    result = await book_use_case.get_all_books(request_payload=request_payload)

    assert len(result.books) == 1
    assert result.books[0].title_rus == unit_test_book_in_db["title_rus"]
    assert result.books[0].authors[0].surname == unit_test_author_in_db["surname"]

    mock_book_repo.get_all_books.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_all_books_bd_error():
    request_payload = BookListQueryParams()

    mock_book_repo = AsyncMock()
    mock_book_repo.get_all_books.side_effect = SQLAlchemyError("DB Error")

    author_use_case = AsyncMock()
    genre_use_case = AsyncMock()
    book_use_case = BookUseCase(
        book_repository=mock_book_repo, author_usecase=author_use_case, genre_usecase=genre_use_case
    )

    with pytest.raises(SQLAlchemyError):
        await book_use_case.get_all_books(request_payload=request_payload)

    mock_book_repo.get_all_books.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_book(unit_test_user, unit_test_book_in_db):
    book_id = 1
    updated_data = BookUpdateSchema(title_rus="Тестовая книга", title_origin="Test Book")

    book_to_update = unit_test_book_in_db
    book_to_update["title_rus"] = updated_data.title_rus
    book_to_update["title_origin"] = updated_data.title_origin
    book_to_update["updated_at"] = datetime.now()
    book_to_update["updated_by"] = unit_test_user["username"]

    mock_book_repo = AsyncMock()
    mock_book_repo.get_book_by_id.return_value = Book(**unit_test_book_in_db)
    mock_book_repo.update_book.return_value = BookReadSchema(**book_to_update)

    author_use_case = AsyncMock()
    genre_use_case = AsyncMock()
    book_use_case = BookUseCase(
        book_repository=mock_book_repo, author_usecase=author_use_case, genre_usecase=genre_use_case
    )

    result = await book_use_case.update_book(
        book_id=book_id, updated_data=updated_data, username=unit_test_user["username"]
    )

    assert result.title_rus == updated_data.title_rus
    assert result.title_origin == updated_data.title_origin
    assert result.updated_by == unit_test_user["username"]

    mock_book_repo.get_book_by_id.assert_awaited_once()
    mock_book_repo.update_book.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_book_db_error(unit_test_user, unit_test_book_in_db):
    book_id = 1
    updated_data = BookUpdateSchema(title_rus="Тестовая книга", title_origin="Test Book")

    mock_book_repo = AsyncMock()
    mock_book_repo.get_book_by_id.return_value = Book(**unit_test_book_in_db)
    mock_book_repo.update_book.side_effect = SQLAlchemyError("DB Error")

    author_use_case = AsyncMock()
    genre_use_case = AsyncMock()
    book_use_case = BookUseCase(
        book_repository=mock_book_repo, author_usecase=author_use_case, genre_usecase=genre_use_case
    )

    with pytest.raises(SQLAlchemyError):
        await book_use_case.update_book(
            book_id=book_id, updated_data=updated_data, username=unit_test_user["username"]
        )

    mock_book_repo.get_book_by_id.assert_awaited_once()
    mock_book_repo.update_book.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_book(unit_test_book_in_db):
    book_id = 1

    mock_book_repo = AsyncMock()
    mock_book_repo.get_book_by_id.return_value = Book(**unit_test_book_in_db)
    mock_book_repo.delete_book.return_value = BookDeleteSchema(
        message=f"Book '{unit_test_book_in_db["title_rus"]}' deleted successfully"
    )

    author_use_case = AsyncMock()
    genre_use_case = AsyncMock()
    book_use_case = BookUseCase(
        book_repository=mock_book_repo, author_usecase=author_use_case, genre_usecase=genre_use_case
    )

    result = await book_use_case.delete_book(book_id=book_id)

    assert result.message == f"Book '{unit_test_book_in_db["title_rus"]}' deleted successfully"

    mock_book_repo.get_book_by_id.assert_awaited_once()
    mock_book_repo.delete_book.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_book_db_error(unit_test_book_in_db):
    book_id = 1

    mock_book_repo = AsyncMock()
    mock_book_repo.get_book_by_id.return_value = Book(**unit_test_book_in_db)
    mock_book_repo.delete_book.side_effect = SQLAlchemyError("DB Error")

    author_use_case = AsyncMock()
    genre_use_case = AsyncMock()
    book_use_case = BookUseCase(
        book_repository=mock_book_repo, author_usecase=author_use_case, genre_usecase=genre_use_case
    )

    with pytest.raises(SQLAlchemyError):
        await book_use_case.delete_book(book_id=book_id)

    mock_book_repo.get_book_by_id.assert_awaited_once()
    mock_book_repo.delete_book.assert_awaited_once()
