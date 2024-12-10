from pydantic import EmailStr
from sqlalchemy.exc import SQLAlchemyError

from configs.logger import logger
from repositories.user_repository import UserRepository


class UserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

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
