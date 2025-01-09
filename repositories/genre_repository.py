from sqlalchemy import select
from sqlalchemy.orm import joinedload

from exception_handlers.genre_exc_handlers import GenreDoesNotExist
from models import Genre
from repositories.abstract_repositories import AbstractGenreRepository
from schemas.genre_schemas import (
    GenreDeleteSchema,
    GenreOrderBy,
    GenreReadSchema,
    GenresListSchema,
)


class GenreRepository(AbstractGenreRepository):
    async def create_new_genre(self, new_genre: Genre) -> Genre:
        self.db.add(new_genre)
        await self.db.commit()
        await self.db.refresh(new_genre)
        return new_genre

    async def get_genre_by_id(self, genre_id: int) -> Genre | None:
        result = await self.db.execute(
            select(Genre).options(joinedload(Genre.books)).where(Genre.id == genre_id)
        )
        genre = result.unique().scalars().first()
        return genre if genre else None

    async def get_genre_by_name(self, name: str) -> Genre | None:
        result = await self.db.execute(select(Genre).where(Genre.name == name))
        genre = result.unique().scalars().first()
        return genre if genre else None

    async def get_all_genres(self, request_payload) -> GenresListSchema:
        query = select(Genre)
        sort_column = getattr(Genre, request_payload.sort_by)

        if request_payload.order_by == GenreOrderBy.desc:
            sort_column = sort_column.desc()

        query = query.order_by(sort_column)

        offset = (request_payload.page - 1) * request_payload.limit
        query = query.offset(offset).limit(request_payload.limit)

        result = await self.db.execute(query)
        genres = result.unique().scalars().all()

        if not genres:
            raise GenreDoesNotExist(message="No genres found")

        genres = [GenreReadSchema.model_validate(genre) for genre in genres]

        return GenresListSchema(genres=genres)

    async def update_genre(self, genre_to_update: Genre) -> Genre:
        await self.db.commit()
        await self.db.refresh(genre_to_update)

        return genre_to_update

    async def delete_genre(self, genre_to_delete: Genre) -> GenreDeleteSchema:
        await self.db.delete(genre_to_delete)
        await self.db.commit()

        return GenreDeleteSchema(message=f"Genre '{genre_to_delete.name}' deleted successfully")
