from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models import Author
from repositories.abstract_repositories import AbstractAuthorRepository


class AuthorRepository(AbstractAuthorRepository):
    async def create_new_author(self, new_author: Author) -> Author:
        pass

    async def get_author_by_id(self, author_id: int) -> Author | None:
        pass

    async def get_author_by_surname(self, surname: str) -> Author | None:
        pass

    async def get_all_authors(self, request_payload):
        pass

    async def update_author(self, author_id: int, update_data):
        pass

    async def delete_author(self, author_id: int):
        pass
