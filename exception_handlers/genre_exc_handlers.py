from fastapi import FastAPI, Request
from starlette import status
from starlette.responses import JSONResponse


class GenreAlreadyExists(Exception):
    def __init__(self, message: str):
        self.detail = message
        super().__init__(self.detail)


class GenreDoesNotExist(Exception):
    def __init__(self, message: str):
        self.detail = message
        super().__init__(self.detail)


def register_genre_exception_handlers(app: FastAPI):
    @app.exception_handler(GenreAlreadyExists)
    async def genre_already_exists_exception_handler(request: Request, exc: GenreAlreadyExists):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.detail},
        )

    @app.exception_handler(GenreDoesNotExist)
    async def genre_does_not_exist_exception_handler(request: Request, exc: GenreDoesNotExist):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.detail},
        )
