from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models import Author
from repositories.abstract_repositories import AbstractAuthorRepository


class AuthorRepository(AbstractAuthorRepository):
    async def create_new_author(self, new_author: Author) -> Author:
        self.db.add(new_author)
        await self.db.commit()
        await self.db.refresh(new_author)
        return new_author

    async def get_author_by_id(self, author_id: int) -> Author | None:
        pass

    async def get_author_by_surname_and_name(self, surname: str, name: str | None) -> Author | None:
        result = await self.db.execute(select(Author).where(Author.surname == surname, Author.name == name))
        author = result.unique().scalars().first()
        return author if author else None

    async def get_all_authors(self, request_payload):
        pass

    async def update_author(self, author_id: int, update_data):
        pass

    async def delete_author(self, author_id: int):
        pass
