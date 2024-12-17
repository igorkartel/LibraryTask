from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class PermissionDeniedError(Exception):
    def __init__(self, message: str):
        self.detail = message
        super().__init__(self.detail)


class TokenError(Exception):
    def __init__(self, message: str):
        self.detail = message
        super().__init__(self.detail)


def register_auth_exception_handlers(app: FastAPI):
    @app.exception_handler(PermissionDeniedError)
    async def permission_denied_exception_handler(request: Request, exc: PermissionDeniedError):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": exc.detail},
        )

    @app.exception_handler(TokenError)
    async def token_error_exception_handler(request: Request, exc: TokenError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": exc.detail},
        )
