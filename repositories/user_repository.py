from pydantic import EmailStr
from sqlalchemy import func, select

from exception_handlers.user_exc_handlers import UserDoesNotExist
from models import User
from repositories.abstract_repositories import AbstractUserRepository
from schemas.user_schemas import (
    UserDeleteSchema,
    UserListQueryParams,
    UserOrderBy,
    UserReadSchema,
    UsersListSchema,
)


class UserRepository(AbstractUserRepository):
    async def create_user(self, new_user: User) -> User:
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        return user if user else None

    async def get_user_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        user = result.unique().scalars().first()
        return user if user else None

    async def get_user_by_email(self, email: EmailStr) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.unique().scalars().first()
        return user if user else None

    async def get_all_users(self, request_payload: UserListQueryParams) -> UsersListSchema:
        query = select(User)
        sort_column = getattr(User, request_payload.sort_by)

        if request_payload.order_by == UserOrderBy.desc:
            sort_column = sort_column.desc()

        query = query.order_by(sort_column)

        offset = (request_payload.page - 1) * request_payload.limit
        query = query.offset(offset).limit(request_payload.limit)

        result = await self.db.execute(query)
        users = result.scalars().all()

        if not users:
            raise UserDoesNotExist(message="No users found")

        users = [UserReadSchema.model_validate(user) for user in users]

        return UsersListSchema(users=users)

    async def update_user(self, current_user_id: int, update_data: dict) -> User:
        result = await self.db.execute(select(User).where(User.id == current_user_id))
        user_to_update = result.scalars().first()

        if not user_to_update:
            raise UserDoesNotExist(message=f"User with id '{current_user_id}' does not exist")

        for key, value in update_data.items():
            setattr(user_to_update, key, value)

        user_to_update.updated_at = func.now()

        await self.db.commit()
        await self.db.refresh(user_to_update)

        return user_to_update

    async def update_user_by_admin(self, user_id: int, update_data: dict) -> User:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user_to_update = result.scalars().first()

        if not user_to_update:
            raise UserDoesNotExist(message=f"User with id '{user_id}' does not exist")

        for key, value in update_data.items():
            setattr(user_to_update, key, value)

        await self.db.commit()
        await self.db.refresh(user_to_update)

        return user_to_update

    async def update_user_password(self, email: EmailStr, new_hashed_password: str):
        result = await self.db.execute(select(User).where(User.email == email))
        user_to_update = result.scalars().first()

        if not user_to_update:
            raise UserDoesNotExist(message=f"User with email '{email}' does not exist")

        user_to_update.password = new_hashed_password
        user_to_update.updated_at = func.now()

        await self.db.commit()
        await self.db.refresh(user_to_update)

        return {"message": "Your password was successfully changed"}

    async def delete_user(self, user_id: int) -> UserDeleteSchema:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user_to_delete = result.scalars().first()

        if not user_to_delete:
            raise UserDoesNotExist(message=f"User with id '{user_id}' does not exist")

        await self.db.delete(user_to_delete)
        await self.db.commit()

        return UserDeleteSchema(message=f"User with id {user_id} deleted successfully")
