from app.routes.astar import router as astar_router
from app.routes.cnn import router as cnn_router
from .routes.fuzzy import router as fuzzy_router

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from pathlib import Path

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
app.include_router(cnn_router)

# Permitir la recuperación de fotografías históricas

CARPETA_CNN = (
    Path(__file__).resolve().parents[1]
    / "uploads"
    / "cnn"
)

CARPETA_CNN.mkdir(parents=True, exist_ok=True)

app.mount(
    "/uploads/cnn",
    StaticFiles(directory=str(CARPETA_CNN)),
    name="imagenes_cnn"
)

@app.get("/")
def inicio():
    return {
        "mensaje": "API del asistente de chile habanero funcionando"
    }
