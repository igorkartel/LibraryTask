from fastapi import APIRouter, Depends

from dependencies.auth_dependencies import get_current_active_user
from dependencies.usecase_dependencies import get_user_usecase
from schemas.user_schemas import UserAdminUpdateSchema, UserReadSchema, UserUpdateSchema
from usecases.user_usecases import UserUseCase

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=UserReadSchema)
async def get_user_me(
    current_user: UserReadSchema = Depends(get_current_active_user),
):
    """Allows the authenticated user with any role to get his user profile information only"""
    return current_user


@router.patch("/me", response_model=UserReadSchema)
async def update_user_me(
    updated_data: UserUpdateSchema,
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: UserUseCase = Depends(get_user_usecase),
):
    """Allows the authenticated user with any role to update his user profile only"""
    return await usecase.update_user(updated_data=updated_data, current_user=current_user)


@router.get("/{user_id}", response_model=UserReadSchema)
async def get_user_by_id(
    user_id: int,
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: UserUseCase = Depends(get_user_usecase),
):
    """Allows the authenticated user with 'ADMIN'-role to get any user by id"""
    return await usecase.get_user_by_id(user_id=user_id, current_user=current_user)


@router.patch("/{user_id}", response_model=UserReadSchema)
async def update_user_by_admin(
    user_id: int,
    updated_data: UserAdminUpdateSchema,
    current_user: UserReadSchema = Depends(get_current_active_user),
    usecase: UserUseCase = Depends(get_user_usecase),
):
    """Allows the authenticated user with 'ADMIN'-role to update any user in the system"""
    return await usecase.update_user_by_admin(
        user_id=user_id, updated_data=updated_data, current_user=current_user
    )


# @router.delete("/me", response_model=UserDeleteSchema)
# async def delete_user_me(
#     user_repository: Annotated[UserRepository, Depends(get_user_repository)],
#     current_user: Annotated[UserReadSchema, Depends(get_current_active_user)],
#     aws_s3_repository: Annotated[AWSS3Repository, Depends(get_aws_s3_repository)],
# ):
#     """Allows the authenticated user with any role to delete his user profile only"""
#     return await user_repository.delete_user(current_user, aws_s3_repository)
