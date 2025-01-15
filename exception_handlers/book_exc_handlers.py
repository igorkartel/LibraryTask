from fastapi import FastAPI, Request
from starlette import status
from starlette.responses import JSONResponse


class BookAlreadyExists(Exception):
    def __init__(self, message: str):
        self.detail = message
        super().__init__(self.detail)


class BookDoesNotExist(Exception):
    def __init__(self, message: str):
        self.detail = message
        super().__init__(self.detail)


def register_book_exception_handlers(app: FastAPI):
    @app.exception_handler(BookAlreadyExists)
    async def book_already_exists_exception_handler(request: Request, exc: BookAlreadyExists):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.detail},
        )

    @app.exception_handler(BookDoesNotExist)
    async def book_does_not_exist_exception_handler(request: Request, exc: BookDoesNotExist):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": exc.detail},
        )
