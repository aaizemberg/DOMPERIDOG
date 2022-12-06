from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import settings
from app.API import login, users, documents

def get_application():
    app = FastAPI(title=settings.PROJECT_NAME)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        html = "<h1>Welcome to DOMPERIDOG</h1><h2>Base de Datos 2 - 2022 2Q - ITBA</h2><p>Integrantes:</p><ul><li>Federico Gustavo Rojas - frojas@itba.edu.ar</li><li>Roberto Franco Rodriguez Tulasne - robrodriguez@itba.edu.ar</li><li>Leonardo Agustín D'Agostino - ldagostino@itba.edu.ar</li></ul><p>Dirigase a /docs para el Swagger de la API</p>"
        return HTMLResponse(html)
    return app


app = get_application()
app.include_router(login.router, prefix="/login", tags=["login"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(users.router, prefix="/users", tags=["users"])