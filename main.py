from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from configs.exception_handlers import register_exception_handlers
# from controllers.routers import auth_routes, healthcheck_route, user_routes, users_route

app = FastAPI()


# register_exception_handlers(app)
#
#
# app.include_router(healthcheck_route.router)
# app.include_router(auth_routes.router)
# app.include_router(user_routes.router)
# app.include_router(users_route.router)


app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)


@app.get("/")
async def root():
    return {"message": "New project"}
