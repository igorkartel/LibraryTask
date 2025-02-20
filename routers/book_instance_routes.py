from fastapi import APIRouter, Depends, File, Path, UploadFile

from dependencies.auth_dependencies import get_current_active_user
from dependencies.usecase_dependencies import get_book_instance_usecase
from schemas.book_schemas import (
    BookInstanceCreateSchema,
    BookInstanceDeleteSchema,
    BookInstanceUpdateSchema,
)
from schemas.common_circular_schemas import (
    BookInstanceWithBookReadSchema,
    BookWithInstancesReadSchema,
)
from schemas.user_schemas import UserReadSchema
from usecases.book_instance_usecases import BookInstanceUseCase

router = APIRouter(prefix="/book_items", tags=["book_items"])


@router.post("/new_item_to_book_id/{book_id}", response_model=BookInstanceWithBookReadSchema)
async def create_new_book_instance(
    book_id: int = Path(...),
    new_book_instance: BookInstanceCreateSchema = Depends(BookInstanceCreateSchema.as_form),
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: BookInstanceUseCase = Depends(get_book_instance_usecase),
    file: UploadFile | None = File(None),
):
    """Allows the authenticated user with any role to create a new book instance to the existing book"""
    return await usecase.create_new_book_instance(
        book_id=book_id, new_book_instance=new_book_instance, file=file, username=current_user.username
    )


@router.get("/{book_instance_id}", response_model=BookInstanceWithBookReadSchema)
async def get_book_instance_by_id(
    book_instance_id: int,
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: BookInstanceUseCase = Depends(get_book_instance_usecase),
):
    """Allows the authenticated user with any role to get any book instance by id"""
    return await usecase.get_book_instance_by_id(book_instance_id=book_instance_id)


@router.get("/all_by_book_id/{book_id}", response_model=BookWithInstancesReadSchema)
async def get_all_instances_by_book_id(
    book_id: int,
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: BookInstanceUseCase = Depends(get_book_instance_usecase),
):
    """Allows the authenticated user with any role to get a book by title with all its instances"""
    return await usecase.get_all_instances_by_book_id(book_id=book_id)


@router.patch("/{book_instance_id}", response_model=BookInstanceWithBookReadSchema)
async def update_book_instance(
    book_instance_id: int,
    updated_data: BookInstanceUpdateSchema = Depends(BookInstanceUpdateSchema.as_form),
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: BookInstanceUseCase = Depends(get_book_instance_usecase),
    file: UploadFile | None = File(None),
):
    """Allows the authenticated user with any role to update a book instance of the existing book"""
    return await usecase.update_book_instance(
        book_instance_id=book_instance_id,
        book_item_to_update=updated_data,
        file=file,
        username=current_user.username,
    )


@router.delete("/{book_instance_id}", response_model=BookInstanceDeleteSchema)
async def delete_book_instance(
    book_instance_id: int,
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: BookInstanceUseCase = Depends(get_book_instance_usecase),
):
    """Allows the authenticated user with any role to delete any book instance in the system"""
    return await usecase.delete_book_instance(book_instance_id=book_instance_id)
