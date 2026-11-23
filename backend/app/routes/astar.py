from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.modules.astar.algorithm import astar, ruta_inspeccion
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
    modo: str = "directa"
    puntos: list[dict] = []


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

    # Verificar los puntos de inspección antes de calcular la ruta.
    if datos.modo not in ("directa", "inspeccion"):
        raise HTTPException(status_code=400, detail="Modo no válido")

    puntos = datos.puntos if datos.modo == "inspeccion" else []
    posiciones = set()
    for punto in puntos:
        posicion = punto.get("posicion")
        prioridad = punto.get("prioridad")
        if (not isinstance(posicion, list) or len(posicion) != 2
                or any(type(n) is not int for n in posicion)
                or prioridad not in ("alta", "media", "baja")):
            raise HTTPException(status_code=400, detail="Punto de inspección inválido")
        f, c = posicion
        if not (0 <= f < len(parcela) and 0 <= c < columnas):
            raise HTTPException(status_code=400, detail="Punto fuera de la parcela")
        if parcela[f][c] != PUNTO_INTERES:
            raise HTTPException(status_code=400, detail="El punto debe estar sobre una celda de interés")
        if (f, c) in posiciones:
            raise HTTPException(status_code=400, detail="Punto de inspección duplicado")
        posiciones.add((f, c))

    if datos.modo == "inspeccion":
        ruta, visitados, inaccesibles = ruta_inspeccion(
            parcela, datos.inicio, datos.destino, puntos
        )
    else:
        ruta = astar(parcela, datos.inicio, datos.destino)
        visitados, inaccesibles = [], []

    if ruta is None:
        return {
            "ruta": None,
            "costo": None,
            "movimientos": 0,
            "mensaje": "No existe una ruta que complete la inspección" if datos.modo == "inspeccion" else "No existe una ruta disponible",
            "puntos_visitados": visitados,
            "puntos_inaccesibles": inaccesibles
        }

    # Cada desplazamiento cuesta una unidad
    costo = len(ruta) - 1

    return {
        "ruta": ruta,
        "costo": costo,
        "movimientos": len(ruta) - 1,
        "mensaje": "Ruta calculada correctamente",
        "puntos_visitados": visitados,
        "puntos_inaccesibles": []
    }
