from abc import ABC, abstractmethod

from aiobotocore.client import AioBaseClient
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
    async def update_user(self, user_to_update):
        pass

    @abstractmethod
    async def update_user_by_admin(self, user_to_update):
        pass

    @abstractmethod
    async def update_user_password(self, user_to_update):
        pass

    @abstractmethod
    async def delete_user(self, user_to_delete):
        pass


class AbstractAuthorRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def create_new_author(self, new_author):
        pass

    @abstractmethod
    async def get_author_by_id(self, author_id):
        pass

    @abstractmethod
    async def get_author_by_surname_and_name(self, surname, name):
        pass

    @abstractmethod
    async def get_all_authors(self, request_payload):
        pass

    @abstractmethod
    async def update_author(self, author_to_update):
        pass

    @abstractmethod
    async def delete_author(self, author_to_delete):
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
    async def update_genre(self, genre_to_update):
        pass

    @abstractmethod
    async def delete_genre(self, genre_to_delete):
        pass


class AbstractBookRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def create_new_book(self, new_book):
        pass

    @abstractmethod
    async def get_book_by_id(self, book_id):
        pass

    @abstractmethod
    async def get_books_by_title(self, book_title):
        pass

    @abstractmethod
    async def get_book_by_title_and_author(self, title, author):
        pass

    @abstractmethod
    async def get_all_books(self, request_payload):
        pass

    @abstractmethod
    async def update_book(self, book_to_update):
        pass

    @abstractmethod
    async def delete_book(self, book_to_delete):
        pass


class AbstractBookInstanceRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def create_new_book_instance(self, new_book_instance):
        pass

    @abstractmethod
    async def get_book_instance_by_id(self, book_instance_id):
        pass

    @abstractmethod
    async def get_all_instances_by_book_title(self, request_payload):
        pass

    @abstractmethod
    async def update_book_instance(self, book_item_to_update):
        pass

    @abstractmethod
    async def delete_book_instance(self, book_item_to_delete):
        pass


class AbstractMinioS3Repository(ABC):
    def __init__(self, s3_client: AioBaseClient):
        self.s3_client = s3_client

    @abstractmethod
    async def ensure_bucket_exists(self, bucket_name):
        pass

    @abstractmethod
    async def create_bucket(self, bucket_name):
        pass

    @abstractmethod
    async def upload_file(self, bucket_name, file):
        pass

    @abstractmethod
    async def delete_file(self, bucket_name, file_name):
        pass
