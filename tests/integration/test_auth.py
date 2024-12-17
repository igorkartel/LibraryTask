from unittest.mock import patch

import pytest
from httpx import AsyncClient
from starlette import status


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_new_user(async_client: AsyncClient, test_user):
    response = await async_client.post("/auth/signup", json=test_user)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "test_user"
    assert "id" in response.json()
    assert "created_at" in response.json()
    assert "updated_at" in response.json()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_for_access_token(async_client: AsyncClient, test_user):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    response = await async_client.post("/auth/login", data=form_data)

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_refresh_access_token(async_client: AsyncClient, test_user):
    form_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = await async_client.post("/auth/login", data=form_data)

    refresh_token = login_response.json()["refresh_token"]

    response = await async_client.post("/auth/refresh-token", params={"refresh_token": refresh_token})

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_forgot_password(async_client: AsyncClient, test_user):
    email = {"email": test_user["email"]}

    with patch("usecases.auth_usecases.send_message_to_rabbitmq") as mock_send_message_to_rabbitmq:
        response = await async_client.post("/auth/forgot-password", json=email)

    assert response.status_code == status.HTTP_200_OK
    assert "reset_token" in response.json()
    assert "message" in response.json()

    mock_send_message_to_rabbitmq.assert_awaited_once()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_reset_password_template(async_client: AsyncClient, test_user):
    email = {"email": test_user["email"]}

    with patch("usecases.auth_usecases.send_message_to_rabbitmq") as mock_send_message_to_rabbitmq:
        response = await async_client.post("/auth/forgot-password", json=email)

    reset_token = response.json()["reset_token"]

    template_response = await async_client.get("/auth/reset-password", params={"reset_token": reset_token})

    assert template_response.status_code == status.HTTP_200_OK
    assert "<html>" in template_response.text
    assert "Reset Password" in template_response.text
    assert f'value="{reset_token}"' in template_response.text


@pytest.mark.integration
@pytest.mark.asyncio
async def test_reset_password(async_client: AsyncClient, test_user):
    email = {"email": test_user["email"]}

    with patch("usecases.auth_usecases.send_message_to_rabbitmq") as mock_send_message_to_rabbitmq:
        response = await async_client.post("/auth/forgot-password", json=email)

    new_credentials = {
        "reset_token": response.json()["reset_token"],
        "new_password": test_user["password"],
        "confirm_new_password": test_user["password"],
    }

    new_pass_response = await async_client.post("/auth/reset-password", json=new_credentials)

    assert new_pass_response.status_code == status.HTTP_200_OK
    assert "message" in new_pass_response.json()
