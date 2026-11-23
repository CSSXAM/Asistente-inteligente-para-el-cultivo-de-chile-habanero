from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.modules.astar.algorithm import astar
from app.modules.astar.grid import (
    PASILLO,
    HILERA_PLANTAS,
    OBSTACULO_FIJO,
    OBSTACULO_TEMPORAL,
    PUNTO_INTERES,
)

router = APIRouter(prefix="/api/astar", tags=["A*"])

TIPOS_VALIDOS = {
    PASILLO,
    HILERA_PLANTAS,
    OBSTACULO_FIJO,
    OBSTACULO_TEMPORAL,
    PUNTO_INTERES,
}

OBSTACULOS = {
    HILERA_PLANTAS,
    OBSTACULO_FIJO,
    OBSTACULO_TEMPORAL,
}


class SolicitudRuta(BaseModel):
    parcela: list[list[int]]
    inicio: tuple[int, int]
    destino: tuple[int, int]


@router.post("/ruta")
def calcular_ruta(datos: SolicitudRuta):
    parcela = datos.parcela

    # Validar que la parcela no esté vacía
    if not parcela or not parcela[0]:
        raise HTTPException(
            status_code=400,
            detail="La parcela no puede estar vacía"
        )

    columnas = len(parcela[0])

    # Comprobar que todas las filas tengan igual longitud
    if any(len(fila) != columnas for fila in parcela):
        raise HTTPException(
            status_code=400,
            detail="Todas las filas deben tener el mismo tamaño"
        )

    # Validar los cinco tipos de celdas
    if any(
        celda not in TIPOS_VALIDOS
        for fila in parcela
        for celda in fila
    ):
        raise HTTPException(
            status_code=400,
            detail="Las celdas deben contener valores entre 0 y 4"
        )

    # Validar las posiciones de inicio y destino
    for posicion in (datos.inicio, datos.destino):
        fila, columna = posicion

        if not (
            0 <= fila < len(parcela)
            and 0 <= columna < columnas
        ):
            raise HTTPException(
                status_code=400,
                detail="Inicio o destino fuera de la parcela"
            )

        if parcela[fila][columna] in OBSTACULOS:
            raise HTTPException(
                status_code=400,
                detail="Inicio o destino sobre una celda no transitable"
            )

    # Ejecutar el algoritmo A*
    ruta = astar(parcela, datos.inicio, datos.destino)

    if ruta is None:
        return {
            "ruta": None,
            "costo": None,
            "movimientos": 0,
            "mensaje": "No existe una ruta disponible"
        }

    # Cada desplazamiento cuesta una unidad
    costo = len(ruta) - 1

    return {
        "ruta": ruta,
        "costo": costo,
        "movimientos": len(ruta) - 1,
        "mensaje": "Ruta calculada correctamente"
    }
