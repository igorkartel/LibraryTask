from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class UserAlreadyExists(Exception):
    def __init__(self, message: str):
        self.detail = message
        super().__init__(self.detail)


class UserDoesNotExist(Exception):
    def __init__(self, message: str):
        self.detail = message
        super().__init__(self.detail)


def register_user_exception_handlers(app: FastAPI):
    @app.exception_handler(UserAlreadyExists)
    async def user_already_exists_exception_handler(request: Request, exc: UserAlreadyExists):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.detail},
        )

    @app.exception_handler(UserDoesNotExist)
    async def user_does_not_exist_exception_handler(request: Request, exc: UserDoesNotExist):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.detail},
        )
