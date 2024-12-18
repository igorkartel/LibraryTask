from fastapi import APIRouter, Depends

from dependencies.auth_dependencies import get_current_active_user
from dependencies.usecase_dependencies import get_genre_usecase
from schemas.common_circular_schemas import GenreWithBooksReadSchema
from schemas.genre_schemas import (
    GenreCreateSchema,
    GenreDeleteSchema,
    GenreListQueryParams,
    GenreReadSchema,
    GenresListSchema,
    GenreUpdateSchema,
)
from schemas.user_schemas import UserReadSchema
from usecases.genre_usecases import GenreUseCase

router = APIRouter(prefix="/genre", tags=["genre"])


@router.post("/new", response_model=GenreReadSchema)
async def create_new_genre(
    new_genre: GenreCreateSchema,
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: GenreUseCase = Depends(get_genre_usecase),
):
    """Allows the authenticated user with any role to create a new genre"""
    return await usecase.create_new_genre(new_genre=new_genre)


@router.get("/{genre_id}", response_model=GenreWithBooksReadSchema)
async def get_genre_by_id(
    genre_id: int,
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: GenreUseCase = Depends(get_genre_usecase),
):
    """Allows the authenticated user with any role to get any genre by id"""
    return await usecase.get_genre_by_id(genre_id=genre_id)


@router.get("/genres/all", response_model=GenresListSchema)
async def get_all_genres(
    request_payload: GenreListQueryParams = Depends(),
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: GenreUseCase = Depends(get_genre_usecase),
):
    """Allows the authenticated user with any role to get all the genres"""
    return await usecase.get_all_genres(request_payload=request_payload)


@router.patch("/{genre_id}", response_model=GenreReadSchema)
async def update_genre(
    genre_id: int,
    updated_data: GenreUpdateSchema,
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: GenreUseCase = Depends(get_genre_usecase),
):
    """Allows the authenticated user with any role to update any genre in the system"""
    return await usecase.update_genre(genre_id=genre_id, updated_data=updated_data)


@router.delete("/{genre_id}", response_model=GenreDeleteSchema)
async def delete_genre(
    genre_id: int,
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: GenreUseCase = Depends(get_genre_usecase),
):
    """Allows the authenticated user with any role to delete any genre in the system"""
    return await usecase.delete_genre(genre_id=genre_id)
