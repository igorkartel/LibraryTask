import pytest
from httpx import AsyncClient
from starlette import status


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_new_book(async_client: AsyncClient, test_user, test_book):
    await async_client.post("/auth/signup", json=test_user)

    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    response = await async_client.post("/book/new_book", json=test_book, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title_rus"] == "Книга"
    assert "id" in response.json()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_map_book_to_existing_authors(
    async_client: AsyncClient, test_user, test_book, test_author, mock_file
):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    author = await async_client.post("/author/new", data=test_author, files=mock_file, headers=headers)

    mapping_request = {"book_id": test_book["id"], "author_ids": [author.json()["id"]]}

    response = await async_client.post("/book/map_to_authors", json=mapping_request, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["authors"] == [author.json()]
    assert response.json()["updated_by"] == test_user["username"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_map_book_to_existing_genres(async_client: AsyncClient, test_user, test_book):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    genre = await async_client.post("/genre/new", json={"name": "Ужасы"}, headers=headers)

    mapping_request = {"book_id": test_book["id"], "genre_ids": [genre.json()["id"]]}

    response = await async_client.post("/book/map_to_genres", json=mapping_request, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["genres"] == [genre.json()]
    assert response.json()["updated_by"] == test_user["username"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_new_book_with_author_and_genre(
    async_client: AsyncClient, test_user, test_book_with_author_and_genre, mock_file
):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    response = await async_client.post(
        "/book/new", data=test_book_with_author_and_genre, files=mock_file, headers=headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_book_with_author_and_genre["id"]
    assert response.json()["created_by"] == test_user["username"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_book_by_id(async_client: AsyncClient, test_user):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    book_id = 2

    response = await async_client.get(f"/book/{book_id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == book_id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_book_by_title(async_client: AsyncClient, test_user, test_book):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    book_title = test_book["title_rus"]

    response = await async_client.get("/book/", params={"book_title": book_title}, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert type(response.json()["books"]) is list
    assert len(response.json()["books"]) == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_all_books(async_client: AsyncClient, test_user, test_book_list_query_params):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    response = await async_client.get("/book/books/all", params=test_book_list_query_params, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["books"]) == 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_book(async_client: AsyncClient, test_user):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    updated_data = {"title_rus": "Оно", "title_origin": "It"}
    book_id = 1

    response = await async_client.patch(f"/book/{book_id}", json=updated_data, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title_rus"] == updated_data["title_rus"]
    assert response.json()["title_origin"] == updated_data["title_origin"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_delete_book(async_client: AsyncClient, test_user, test_book_with_author_and_genre):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    book_id = 2

    response = await async_client.delete(f"/book/{book_id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.json()["message"]
        == f"Book '{test_book_with_author_and_genre["title_rus"]}' deleted successfully"
    )
