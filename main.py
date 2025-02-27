from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from exception_handlers.auth_exc_handlers import register_auth_exception_handlers
from exception_handlers.author_exc_handlers import register_author_exception_handlers
from exception_handlers.book_exc_handlers import register_book_exception_handlers
from exception_handlers.db_exc_handlers import register_db_exception_handlers
from exception_handlers.genre_exc_handlers import register_genre_exception_handlers
from exception_handlers.minio_s3_exc_handlers import register_minio_exception_handlers
from exception_handlers.user_exc_handlers import register_user_exception_handlers
from routers import (
    auth_routes,
    author_routes,
    book_instance_routes,
    book_routes,
    genre_routes,
    user_routes,
)

app = FastAPI()

# Register all the exception handlers
register_auth_exception_handlers(app)
register_db_exception_handlers(app)
register_minio_exception_handlers(app)
register_user_exception_handlers(app)
register_author_exception_handlers(app)
register_genre_exception_handlers(app)
register_book_exception_handlers(app)

# Register all the routers
# app.include_router(healthcheck_route.router)
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(author_routes.router)
app.include_router(genre_routes.router)
app.include_router(book_routes.router)
app.include_router(book_instance_routes.router)

# Middleware
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)


@app.get("/")
async def root():
    return {"message": "New project"}
