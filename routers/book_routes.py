from fastapi import APIRouter, Depends, File, UploadFile

from dependencies.auth_dependencies import get_current_active_user
from dependencies.usecase_dependencies import get_book_usecase
from schemas.book_schemas import (
    BookDeleteSchema,
    BookListQueryParams,
    BookReadSchema,
    BookUpdateSchema,
    BookWithAuthorsGenresCreateSchema,
)
from schemas.common_circular_schemas import (
    BookListSchema,
    BookWithAuthorsGenresReadSchema,
)
from schemas.user_schemas import UserReadSchema
from usecases.book_usecases import BookUseCase

router = APIRouter(prefix="/book", tags=["book"])


@router.post("/new", response_model=BookWithAuthorsGenresReadSchema)
async def create_new_book_with_author_and_genre(
    new_book: BookWithAuthorsGenresCreateSchema = Depends(BookWithAuthorsGenresCreateSchema.as_form),
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: BookUseCase = Depends(get_book_usecase),
    file: UploadFile | None = File(None),
):
    """
    Allows the authenticated user with any role to create a new book, to map it to existing authors and genres or
    to create new author and genre for this book if no existing
    """
    return await usecase.create_new_book_with_author_and_genre(
        new_book=new_book, file=file, username=current_user.username
    )


@router.get("/{book_id}", response_model=BookWithAuthorsGenresReadSchema)
async def get_book_by_id(
    book_id: int,
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: BookUseCase = Depends(get_book_usecase),
):
    """Allows the authenticated user with any role to get any book by id"""
    return await usecase.get_book_by_id(book_id=book_id)


@router.get("/", response_model=BookListSchema)
async def get_books_by_title(
    book_title: str,
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: BookUseCase = Depends(get_book_usecase),
):
    """Allows the authenticated user with any role to get books by title"""
    return await usecase.get_books_by_title(book_title=book_title)


@router.get("/books/all", response_model=BookListSchema)
async def get_all_books(
    request_payload: BookListQueryParams = Depends(),
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: BookUseCase = Depends(get_book_usecase),
):
    """Allows the authenticated user with any role to get all the books"""
    return await usecase.get_all_books(request_payload=request_payload)


@router.patch("/{book_id}", response_model=BookReadSchema)
async def update_book(
    book_id: int,
    updated_data: BookUpdateSchema,
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: BookUseCase = Depends(get_book_usecase),
):
    """Allows the authenticated user with any role to update any book in the system"""
    return await usecase.update_book(
        book_id=book_id, updated_data=updated_data, username=current_user.username
    )


@router.delete("/{book_id}", response_model=BookDeleteSchema)
async def delete_book(
    book_id: int,
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: BookUseCase = Depends(get_book_usecase),
):
    """Allows the authenticated user with any role to delete any book in the system"""
    return await usecase.delete_book(book_id=book_id)
