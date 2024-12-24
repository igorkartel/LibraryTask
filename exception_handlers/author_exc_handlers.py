from fastapi import FastAPI, Request
from starlette import status
from starlette.responses import JSONResponse


class AuthorAlreadyExists(Exception):
    def __init__(self, message: str):
        self.detail = message
        super().__init__(self.detail)


class AuthorDoesNotExist(Exception):
    def __init__(self, message: str):
        self.detail = message
        super().__init__(self.detail)


def register_author_exception_handlers(app: FastAPI):
    @app.exception_handler(AuthorAlreadyExists)
    async def author_already_exists_exception_handler(request: Request, exc: AuthorAlreadyExists):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.detail},
        )

    @app.exception_handler(AuthorDoesNotExist)
    async def author_does_not_exist_exception_handler(request: Request, exc: AuthorDoesNotExist):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.detail},
        )
