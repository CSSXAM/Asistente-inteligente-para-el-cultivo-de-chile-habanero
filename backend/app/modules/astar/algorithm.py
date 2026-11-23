# Representación de la parcela, obstáculos y surcos prioritarios.

import heapq

from app.modules.astar.grid import (
    PASILLO,
    HILERA_PLANTAS,
    OBSTACULO_FIJO,
    OBSTACULO_TEMPORAL,
    PUNTO_INTERES,
)

OBSTACULOS = {
    HILERA_PLANTAS,
    OBSTACULO_FIJO,
    OBSTACULO_TEMPORAL,
}

COSTOS = {
    PASILLO: 1,
    PUNTO_INTERES: 1,
}


def heuristica(actual, destino):
    return (
        abs(actual[0] - destino[0])
        + abs(actual[1] - destino[1])
    )


def astar(parcela, inicio, destino):
    filas = len(parcela)
    columnas = len(parcela[0])

    if parcela[inicio[0]][inicio[1]] in OBSTACULOS:
        return None

    if parcela[destino[0]][destino[1]] in OBSTACULOS:
        return None

    abiertos = []
    heapq.heappush(abiertos, (0, inicio))

    anteriores = {}
    costos_acumulados = {inicio: 0}

    movimientos = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
    ]

    while abiertos:
        _, actual = heapq.heappop(abiertos)

        if actual == destino:
            ruta = [actual]

            while actual in anteriores:
                actual = anteriores[actual]
                ruta.append(actual)

            return ruta[::-1]

        for movimiento_fila, movimiento_columna in movimientos:
            nueva_fila = actual[0] + movimiento_fila
            nueva_columna = actual[1] + movimiento_columna

            if not (
                0 <= nueva_fila < filas
                and 0 <= nueva_columna < columnas
            ):
                continue

            tipo_celda = parcela[nueva_fila][nueva_columna]

            if tipo_celda in OBSTACULOS:
                continue

            vecino = (nueva_fila, nueva_columna)

            nuevo_costo = (
                costos_acumulados[actual]
                + COSTOS[tipo_celda]
            )

            if (
                vecino not in costos_acumulados
                or nuevo_costo < costos_acumulados[vecino]
            ):
                costos_acumulados[vecino] = nuevo_costo
                anteriores[vecino] = actual

                prioridad = (
                    nuevo_costo
                    + heuristica(vecino, destino)
                )

                heapq.heappush(
                    abiertos,
                    (prioridad, vecino)
                )

    return None
