from pydantic import EmailStr
from sqlalchemy import select

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

    # async def update_user_password(self, new_credentials: UserResetPasswordSchema):
    #     await update_user_password_service(self.db, new_credentials)
    #     return {"message": "Your password was successfully changed"}
