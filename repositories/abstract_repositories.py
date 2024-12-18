from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession


class AbstractUserRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def create_user(self, new_user):
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id):
        pass

    @abstractmethod
    async def get_user_by_username(self, username):
        pass

    @abstractmethod
    async def get_user_by_email(self, email):
        pass

    @abstractmethod
    async def get_all_users(self, request_payload):
        pass

    @abstractmethod
    async def update_user(self, current_user, update_data):
        pass

    @abstractmethod
    async def update_user_by_admin(self, user_id, update_data):
        pass

    @abstractmethod
    async def update_user_password(self, email, new_hashed_password):
        pass

    @abstractmethod
    async def delete_user(self, user_id):
        pass


class AbstractGenreRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def create_new_genre(self, new_genre):
        pass

    @abstractmethod
    async def get_genre_by_id(self, genre_id):
        pass

    @abstractmethod
    async def get_genre_by_name(self, name):
        pass

    @abstractmethod
    async def get_all_genres(self, request_payload):
        pass

    @abstractmethod
    async def update_genre(self, genre_id, update_data):
        pass

    @abstractmethod
    async def delete_genre(self, genre_id):
        pass
