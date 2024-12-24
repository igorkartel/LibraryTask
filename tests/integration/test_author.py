import pytest
from httpx import AsyncClient
from starlette import status


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_new_author(async_client: AsyncClient, test_user, test_author, mock_file):
    await async_client.post("/auth/signup", json=test_user)

    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    response = await async_client.post("/author/new", data=test_author, files=mock_file, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["surname"] == "Кинг"
    assert "id" in response.json()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_author_by_id(async_client: AsyncClient, test_user):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    author_id = 1

    response = await async_client.get(f"/author/{author_id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == author_id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_all_authors(async_client: AsyncClient, test_user, test_author_list_query_params):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    response = await async_client.get(
        "/author/authors/all", params=test_author_list_query_params, headers=headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["authors"]) == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_author(async_client: AsyncClient, test_user, mock_file):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    updated_data = {"name": "Лев", "surname": "Толстой", "nationality": "Россия"}
    author_id = 1

    response = await async_client.patch(
        f"/author/{author_id}", data=updated_data, files=mock_file, headers=headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == updated_data["name"]
    assert response.json()["surname"] == updated_data["surname"]
    assert response.json()["nationality"] == updated_data["nationality"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_delete_author(async_client: AsyncClient, test_user):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    author_to_delete = {"name": "Лев", "surname": "Толстой"}
    author_id = 1

    response = await async_client.delete(f"/author/{author_id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.json()["message"]
        == f"Author '{author_to_delete["name"]} {author_to_delete["surname"]}' deleted successfully"
    )
