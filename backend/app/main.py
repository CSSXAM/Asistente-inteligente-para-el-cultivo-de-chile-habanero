from app.routes.astar import router as astar_router

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.fuzzy import router as fuzzy_router

app = FastAPI(title="Asistente IA - Chile Habanero")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(astar_router)
app.include_router(fuzzy_router)

@app.get("/")
def inicio():
    return {
        "mensaje": "API del asistente de chile habanero funcionando"
    }
