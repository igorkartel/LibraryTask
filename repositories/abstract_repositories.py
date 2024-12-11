from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession


class AbstractUserRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def create_user(self, new_user):
        pass

    # @abstractmethod
    # async def get_user_by_id(self, current_user, user_id):
    #     pass
    #
    @abstractmethod
    async def get_user_by_username(self, username):
        pass

    @abstractmethod
    async def get_user_by_email(self, email):
        pass

    #
    # @abstractmethod
    # async def get_all_users(self, current_user, request_payload):
    #     pass
    #
    # @abstractmethod
    # async def update_user(self, current_user, update_data):
    #     pass
    #
    # @abstractmethod
    # async def update_user_by_admin(self, current_user, user_id, update_data):
    #     pass
    #
    # @abstractmethod
    # async def delete_user(self, current_user):
    #     pass
    #
    @abstractmethod
    async def update_user_password(self, email, new_hashed_password):
        pass
