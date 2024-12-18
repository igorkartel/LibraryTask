import pytest
from httpx import AsyncClient
from starlette import status


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_new_genre(async_client: AsyncClient, test_user):
    await async_client.post("/auth/signup", json=test_user)

    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    response = await async_client.post("/genre/new", json={"name": "Фантастика"}, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Фантастика"
    assert "id" in response.json()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_genre_by_id(async_client: AsyncClient, test_user):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    genre_id = 1

    response = await async_client.get(f"/genre/{genre_id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == genre_id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_all_genres(async_client: AsyncClient, test_user, test_genre_list_query_params):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    response = await async_client.get(
        "/genre/genres/all", params=test_genre_list_query_params, headers=headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["genres"]) == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_genre(async_client: AsyncClient, test_user):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    updated_data = {"name": "Научная фантастика"}
    genre_id = 1

    response = await async_client.patch(f"/genre/{genre_id}", json=updated_data, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == updated_data["name"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_delete_genre(async_client: AsyncClient, test_user):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    genre_to_delete = {"name": "Научная фантастика"}
    genre_id = 1

    response = await async_client.delete(f"/genre/{genre_id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == f"Genre '{genre_to_delete["name"]}' deleted successfully"
