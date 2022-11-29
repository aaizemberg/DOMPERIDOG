from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import settings
from app.API import documents, login, users

def get_application():
    app = FastAPI(title=settings.PROJECT_NAME)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = get_application()
app.include_router(login.router, prefix="/login", tags=["login"])
# app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(users.router, prefix="/users", tags=["users"])