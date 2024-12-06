from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserForgotPasswordSchema(BaseModel):
    email: EmailStr = Field(example="user@example.com")


class UserResetPasswordSchema(BaseModel):
    reset_token: str
    new_password: str = Field(min_length=8)
    confirm_new_password: str = Field(min_length=8)
