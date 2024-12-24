from pydantic import EmailStr
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from configs.logger import logger
from exception_handlers.auth_exc_handlers import PermissionDeniedError
from exception_handlers.user_exc_handlers import UserDoesNotExist
from models.user_role_enum import UserRoleEnum
from repositories.user_repository import UserRepository
from schemas.user_schemas import (
    UserAdminUpdateSchema,
    UserListQueryParams,
    UserReadSchema,
    UserUpdateSchema,
)


class UserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_user_by_id(self, user_id: int, current_user: UserReadSchema):
        try:
            if current_user.role != UserRoleEnum.ADMIN:
                raise PermissionDeniedError(message="You have no permission to get User's data")

            get_user = await self.user_repository.get_user_by_id(user_id=user_id)

            if not get_user:
                raise UserDoesNotExist(message=f"User with id '{user_id}' does not exist")

            return get_user

        except SQLAlchemyError as exc:
            logger.error(f"Failed to fetch user by id: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def get_user_by_username(self, username: str):
        try:
            user = await self.user_repository.get_user_by_username(username=username)

            if not user:
                return

            return user

        except SQLAlchemyError as exc:
            logger.error(f"Failed to fetch user by username: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def get_user_by_email(self, email: EmailStr):
        try:
            user = await self.user_repository.get_user_by_email(email=email)

            if not user:
                return

            return user

        except SQLAlchemyError as exc:
            logger.error(f"Failed to fetch user by email: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def get_all_users(self, request_payload: UserListQueryParams, current_user: UserReadSchema):
        try:
            if current_user.role != UserRoleEnum.ADMIN:
                raise PermissionDeniedError(message="You have no permission to get the list of all users")

            return await self.user_repository.get_all_users(request_payload=request_payload)

        except SQLAlchemyError as exc:
            logger.error(f"Failed to fetch users' list: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def update_user(self, updated_data: UserUpdateSchema, current_user: UserReadSchema):
        try:
            user_to_update = await self.user_repository.get_user_by_id(user_id=current_user.id)

            if not user_to_update:
                raise UserDoesNotExist(message=f"User with id '{current_user.id}' does not exist")

            update_data_dict = updated_data.model_dump(exclude_unset=True)

            for key, value in update_data_dict.items():
                setattr(user_to_update, key, value)

            user_to_update.updated_at = func.now()

            return await self.user_repository.update_user(user_to_update=user_to_update)

        except SQLAlchemyError as exc:
            logger.error(f"Failed to update user: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def update_user_by_admin(
        self, user_id: int, updated_data: UserAdminUpdateSchema, current_user: UserReadSchema
    ):
        try:
            if current_user.role != UserRoleEnum.ADMIN:
                raise PermissionDeniedError(message="You have no permission to update any User's data")

            user_to_update = await self.user_repository.get_user_by_id(user_id=user_id)

            if not user_to_update:
                raise UserDoesNotExist(message=f"User with id '{user_id}' does not exist")

            update_data_dict = updated_data.model_dump(exclude_unset=True)

            for key, value in update_data_dict.items():
                setattr(user_to_update, key, value)

            user_to_update.updated_at = func.now()

            return await self.user_repository.update_user_by_admin(user_to_update=user_to_update)

        except SQLAlchemyError as exc:
            logger.error(f"Failed to update user: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def delete_user(self, user_id: int, current_user: UserReadSchema):
        try:
            if current_user.role != UserRoleEnum.ADMIN:
                raise PermissionDeniedError(message="You have no permission to update any User's data")

            user_to_delete = await self.user_repository.get_user_by_id(user_id=user_id)

            if not user_to_delete:
                raise UserDoesNotExist(message=f"User with id '{user_id}' does not exist")

            return await self.user_repository.delete_user(user_to_delete=user_to_delete)

        except SQLAlchemyError as exc:
            logger.error(f"Failed to delete user: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise
