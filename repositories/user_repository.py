from pydantic import EmailStr
from sqlalchemy import func, select

from exception_handlers.user_exc_handlers import UserDoesNotExist
from models import User
from repositories.abstract_repositories import AbstractUserRepository


class UserRepository(AbstractUserRepository):
    async def create_user(self, new_user: User) -> User:
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def get_user_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        user = result.unique().scalars().first()
        return user if user else None

    async def get_user_by_email(self, email: EmailStr) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.unique().scalars().first()
        return user if user else None

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
