from fastapi import APIRouter, Depends, File, UploadFile

from dependencies.auth_dependencies import get_current_active_user
from dependencies.usecase_dependencies import get_author_usecase
from schemas.author_schemas import (
    AuthorCreateSchema,
    AuthorDeleteSchema,
    AuthorListQueryParams,
    AuthorReadSchema,
    AuthorsListSchema,
    AuthorUpdateSchema,
)
from schemas.common_circular_schemas import AuthorWithBooksReadSchema
from schemas.user_schemas import UserReadSchema
from usecases.author_usecases import AuthorUseCase

router = APIRouter(prefix="/author", tags=["author"])


@router.post("/new", response_model=AuthorReadSchema)
async def create_new_author(
    new_author: AuthorCreateSchema = Depends(AuthorCreateSchema.as_form),
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: AuthorUseCase = Depends(get_author_usecase),
    file: UploadFile | None = File(None),
):
    """Allows the authenticated user with any role to create a new author"""
    return await usecase.create_new_author(new_author=new_author, file=file, username=current_user.username)


@router.get("/{author_id}", response_model=AuthorWithBooksReadSchema)
async def get_author_by_id(
    author_id: int,
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: AuthorUseCase = Depends(get_author_usecase),
):
    """Allows the authenticated user with any role to get any author by id"""
    return await usecase.get_author_by_id(author_id=author_id)


@router.get("/authors/all", response_model=AuthorsListSchema)
async def get_all_authors(
    request_payload: AuthorListQueryParams = Depends(),
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: AuthorUseCase = Depends(get_author_usecase),
):
    """Allows the authenticated user with any role to get all the authors"""
    return await usecase.get_all_authors(request_payload=request_payload)


@router.patch("/{author_id}", response_model=AuthorReadSchema)
async def update_author(
    author_id: int,
    updated_data: AuthorUpdateSchema = Depends(AuthorUpdateSchema.as_form),
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: AuthorUseCase = Depends(get_author_usecase),
    file: UploadFile = File(None),
):
    """Allows the authenticated user with any role to update any author in the system"""
    return await usecase.update_author(
        author_id=author_id, updated_data=updated_data, file=file, username=current_user.username
    )


@router.delete("/{author_id}", response_model=AuthorDeleteSchema)
async def delete_author(
    author_id: int,
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: AuthorUseCase = Depends(get_author_usecase),
):
    """Allows the authenticated user with any role to delete any author in the system"""
    return await usecase.delete_author(author_id=author_id)
