from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..modules.fuzzy.controller import calcular_riego

router = APIRouter(
    prefix="/api/fuzzy",
    tags=["Lógica difusa"]
)


class SolicitudRiego(BaseModel):
    humedad: float = Field(ge=0, le=100)
    temperatura: float = Field(ge=0, le=50)
    etapa: int = Field(ge=1, le=6, strict=True)


@router.post("/riego")
async def recomendar_riego(datos: SolicitudRiego):
    try:
        resultado = calcular_riego(
            humedad_actual=datos.humedad,
            temperatura_actual=datos.temperatura,
            etapa_actual=datos.etapa
        )

        return resultado

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )