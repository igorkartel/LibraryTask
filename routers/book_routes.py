from fastapi import APIRouter, Depends, File, UploadFile

from dependencies.auth_dependencies import get_current_active_user
from dependencies.usecase_dependencies import get_book_usecase
from schemas.book_schemas import BookWithAuthorsGenresCreateSchema
from schemas.common_circular_schemas import BookWithAuthorsGenresReadSchema
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
