from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo
from starlette import status


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserForgotPasswordSchema(BaseModel):
    email: EmailStr


class UserResetPasswordSchema(BaseModel):
    reset_token: str
    new_password: str = Field(min_length=8)
    confirm_new_password: str = Field(min_length=8)

    @field_validator("confirm_new_password")
    def passwords_match(cls, confirm_new_password: str, values: FieldValidationInfo):
        new_password = values.data.get("new_password")
        if new_password != confirm_new_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
        return confirm_new_password
