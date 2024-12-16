import pytest
from httpx import AsyncClient
from starlette import status


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_user_me(async_client: AsyncClient, test_user):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get("/user/me", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == test_user["username"]
    assert response.json()["email"] == test_user["email"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_user_me(async_client: AsyncClient, test_user_2, test_user_2_for_update):
    await async_client.post("/auth/signup", json=test_user_2)

    form_data = {"username": test_user_2["username"], "password": test_user_2["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.patch("/user/me", json=test_user_2_for_update, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == test_user_2_for_update["email"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_user_by_id(async_client: AsyncClient, test_user, test_user_2):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    user_id = test_user_2["id"]
    response = await async_client.get(f"/user/{user_id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == test_user_2["username"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_all_users(async_client: AsyncClient, test_user, test_user_list_query_params):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get("/user/users/all", params=test_user_list_query_params, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["users"]) == 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_user_by_admin(
    async_client: AsyncClient, test_user, test_user_3, test_user_3_for_update
):
    await async_client.post("/auth/signup", json=test_user_3)

    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    user_id = test_user_3["id"]
    response = await async_client.patch(f"/user/{user_id}", json=test_user_3_for_update, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_blocked"] == test_user_3_for_update["is_blocked"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_delete_user(async_client: AsyncClient, test_user, test_user_3):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    user_id = test_user_3["id"]
    response = await async_client.delete(f"/user/{user_id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == f"User with id {user_id} deleted successfully"
