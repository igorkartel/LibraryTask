from datetime import datetime

from pydantic import EmailStr
from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[EmailStr] = mapped_column(String, unique=True, nullable=False)
    role: Mapped[str] = mapped_column(default="librarian")
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now, onupdate=func.now)

    def __str__(self):
        return self.username
