from fastapi import APIRouter, Depends, File, UploadFile

from dependencies.auth_dependencies import get_current_active_user
from dependencies.usecase_dependencies import get_author_usecase
from schemas.author_schemas import AuthorCreateSchema, AuthorReadSchema
from schemas.user_schemas import UserReadSchema
from usecases.author_usecases import AuthorUseCase

router = APIRouter(prefix="/author", tags=["author"])


@router.post("/new", response_model=AuthorReadSchema)
async def create_new_author(
    new_author: AuthorCreateSchema,
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: AuthorUseCase = Depends(get_author_usecase),
    file: UploadFile = File(None),
):
    """Allows the authenticated user with any role to create a new author"""
    return await usecase.create_new_author(new_author=new_author, file=file, username=current_user.username)
