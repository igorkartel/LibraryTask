from sqlalchemy import select
from sqlalchemy.orm import joinedload

from exception_handlers.author_exc_handlers import AuthorDoesNotExist
from models import Author
from repositories.abstract_repositories import AbstractAuthorRepository
from schemas.author_schemas import (
    AuthorDeleteSchema,
    AuthorListQueryParams,
    AuthorOrderBy,
    AuthorReadSchema,
    AuthorsListSchema,
)


class AuthorRepository(AbstractAuthorRepository):
    async def create_new_author(self, new_author: Author) -> Author:
        self.db.add(new_author)
        await self.db.commit()
        await self.db.refresh(new_author)
        return new_author

    async def get_author_by_id(self, author_id: int) -> Author | None:
        result = await self.db.execute(
            select(Author).options(joinedload(Author.books)).where(Author.id == author_id)
        )
        author = result.unique().scalars().first()

        return author if author else None

    async def get_author_by_surname_and_name(self, surname: str, name: str | None) -> Author | None:
        if not name:
            result = await self.db.execute(select(Author).where(Author.surname == surname))
        else:
            result = await self.db.execute(
                select(Author).where(Author.surname == surname, Author.name == name)
            )

        author = result.unique().scalars().first()

        return author if author else None

    async def get_all_authors(self, request_payload: AuthorListQueryParams) -> AuthorsListSchema:
        query = select(Author)
        sort_column = getattr(Author, request_payload.sort_by)

        if request_payload.order_by == AuthorOrderBy.desc:
            sort_column = sort_column.desc()

        query = query.order_by(sort_column)

        offset = (request_payload.page - 1) * request_payload.limit
        query = query.offset(offset).limit(request_payload.limit)

        result = await self.db.execute(query)
        authors = result.unique().scalars().all()

        if not authors:
            raise AuthorDoesNotExist(message="No authors found")

        authors = [AuthorReadSchema.model_validate(author) for author in authors]

        return AuthorsListSchema(authors=authors)

    async def update_author(self, author_to_update: Author) -> Author:
        await self.db.commit()
        await self.db.refresh(author_to_update)

        return author_to_update

    async def delete_author(self, author_to_delete: Author) -> AuthorDeleteSchema:
        await self.db.delete(author_to_delete)
        await self.db.commit()

        return AuthorDeleteSchema(
            message=f"Author '{author_to_delete.name} {author_to_delete.surname}' deleted successfully"
        )
