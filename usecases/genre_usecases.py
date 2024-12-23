from sqlalchemy.exc import SQLAlchemyError

from configs.logger import logger
from exception_handlers.genre_exc_handlers import GenreAlreadyExists, GenreDoesNotExist
from models import Genre
from repositories.genre_repository import GenreRepository
from schemas.genre_schemas import (
    GenreCreateSchema,
    GenreListQueryParams,
    GenreUpdateSchema,
)


class GenreUseCase:
    def __init__(self, genre_repository: GenreRepository):
        self.genre_repository = genre_repository

    async def create_new_genre(self, new_genre: GenreCreateSchema):
        try:
            new_genre_name = new_genre.name.capitalize()
            existing_genre = await self.genre_repository.get_genre_by_name(name=new_genre_name)
            if existing_genre:
                raise GenreAlreadyExists(message=f"Genre '{new_genre_name}' already exists")

            new_genre.name = new_genre_name
            new_genre = Genre(**new_genre.model_dump())

            return await self.genre_repository.create_new_genre(new_genre=new_genre)

        except SQLAlchemyError as exc:
            logger.error(f"Failed to create a new genre: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def get_genre_by_id(self, genre_id: int):
        try:
            genre = await self.genre_repository.get_genre_by_id(genre_id=genre_id)

            if not genre:
                raise GenreDoesNotExist(message=f"Genre with id '{genre_id}' does not exist")

            return genre

        except SQLAlchemyError as exc:
            logger.error(f"Failed to fetch genre by id: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def get_genre_by_name(self, name: str):
        try:
            genre = await self.genre_repository.get_genre_by_name(name=name)

            if not genre:
                return

            return genre

        except SQLAlchemyError as exc:
            logger.error(f"Failed to fetch genre by name: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def get_all_genres(self, request_payload: GenreListQueryParams):
        try:
            return await self.genre_repository.get_all_genres(request_payload=request_payload)

        except SQLAlchemyError as exc:
            logger.error(f"Failed to fetch genres' list: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def update_genre(self, genre_id: int, updated_data: GenreUpdateSchema):
        try:
            update_data_dict = updated_data.model_dump(exclude_unset=True)
            update_data_dict["name"] = updated_data.name.capitalize()

            genre_to_update = await self.genre_repository.get_genre_by_id(genre_id=genre_id)

            if not genre_to_update:
                raise GenreDoesNotExist(message=f"Genre with id '{genre_id}' does not exist")

            for key, value in update_data_dict.items():
                setattr(genre_to_update, key, value)

            return await self.genre_repository.update_genre(genre_to_update=genre_to_update)

        except SQLAlchemyError as exc:
            logger.error(f"Failed to update genre: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise

    async def delete_genre(self, genre_id: int):
        try:
            genre_to_delete = await self.genre_repository.get_genre_by_id(genre_id=genre_id)

            if not genre_to_delete:
                raise GenreDoesNotExist(message=f"Genre with id '{genre_id}' does not exist")

            return await self.genre_repository.delete_genre(genre_to_delete=genre_to_delete)

        except SQLAlchemyError as exc:
            logger.error(f"Failed to delete genre: {str(exc)}")
            raise SQLAlchemyError
        except Exception as exc:
            logger.error(str(exc))
            raise
