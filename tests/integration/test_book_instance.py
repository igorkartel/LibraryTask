import pytest
from httpx import AsyncClient
from starlette import status


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_new_book_instance(
    async_client: AsyncClient, test_user, test_author, test_book, test_book_instance, mock_file
):
    await async_client.post("/auth/signup", json=test_user)

    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    book = await async_client.post("/book/new_book", json=test_book, headers=headers)
    author_id = 2

    mapping_request = {"book_id": book.json()["id"], "author_ids": [author_id]}

    await async_client.post("/book/map_to_authors", json=mapping_request, headers=headers)

    response = await async_client.post(
        f"/book_items/new_item_to_book_id/{book.json()["id"]}",
        data=test_book_instance,
        files=mock_file,
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["imprint_year"] == test_book_instance["imprint_year"]
    assert "id" in response.json()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_book_instance_by_id(async_client: AsyncClient, test_user, test_book_instance):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    response = await async_client.get(f"/book_items/{test_book_instance["id"]}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_book_instance["id"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_all_instances_by_book_id(async_client: AsyncClient, test_user, test_book):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    book_id = 3

    response = await async_client.get(f"/book_items/all_by_book_id/{book_id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == book_id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_book_instance(async_client: AsyncClient, test_user, mock_file):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    updated_data = {"pages": 400, "value": 60}
    book_instance_id = 1

    response = await async_client.patch(
        f"/book_items/{book_instance_id}", data=updated_data, files=mock_file, headers=headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["pages"] == updated_data["pages"]
    assert response.json()["value"] == updated_data["value"]
    assert response.json()["price_per_day"] == updated_data["value"] / 30


@pytest.mark.integration
@pytest.mark.asyncio
async def test_delete_book_instance(async_client: AsyncClient, test_user, test_book):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    book_instance_id = 1

    response = await async_client.delete(f"/book_items/{book_instance_id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.json()["message"]
        == f"Book item of the book '{test_book["title_rus"]}' deleted successfully"
    )
