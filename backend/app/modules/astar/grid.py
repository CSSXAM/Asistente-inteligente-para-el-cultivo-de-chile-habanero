# Implementación de A* para calcular rutas.
# Tipos de celdas de la parcela
PASILLO = 0
HILERA_PLANTAS = 1
OBSTACULO_FIJO = 2
OBSTACULO_TEMPORAL = 3
PUNTO_INTERES = 4

# Parcela de ejemplo: 6 filas x 6 columnas
parcela = [
    [0, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 0],
    [0, 1, 0, 1, 0, 0],
    [0, 1, 0, 1, 0, 0],
    [0, 1, 0, 1, 4, 0],
    [0, 0, 0, 0, 0, 0],
]

inicio = (0, 0)
destino = (4, 4)