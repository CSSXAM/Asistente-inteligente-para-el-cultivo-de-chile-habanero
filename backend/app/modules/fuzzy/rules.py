
from skfuzzy import control as ctrl

from .variables import humedad, temperatura, etapa, riego


# ==========================================
# ORDEN DE LAS VARIABLES
# ==========================================

HUMEDADES = [
    'muy_seca',
    'seca',
    'moderada',
    'optima',
    'muy_humeda'
]

TEMPERATURAS = [
    'fria',
    'templada',
    'optima',
    'caliente',
    'muy_caliente'
]

SALIDAS = {
    0: 'nulo',
    1: 'muy_corto',
    2: 'corto',
    3: 'medio',
    4: 'largo',
    5: 'muy_largo'
}


# ==========================================
# MATRICES DE DECISIÓN
# ==========================================

MATRICES = {

    'vivero': [
        [2, 3, 3, 4, 4],
        [1, 2, 2, 3, 3],
        [0, 1, 1, 2, 2],
        [0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0]
    ],

    'trasplante': [
        [3, 4, 5, 5, 5],
        [2, 3, 4, 4, 5],
        [1, 2, 3, 3, 4],
        [0, 0, 1, 1, 2],
        [0, 0, 0, 0, 0]
    ],

    'vegetativo': [
        [3, 3, 4, 5, 5],
        [2, 2, 3, 4, 4],
        [1, 1, 2, 3, 3],
        [0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0]
    ],

    'floracion': [
        [3, 4, 5, 5, 5],
        [2, 3, 4, 4, 5],
        [1, 2, 3, 4, 4],
        [0, 0, 1, 2, 2],
        [0, 0, 0, 0, 0]
    ],

    'fructificacion': [
        [3, 4, 5, 5, 5],
        [2, 3, 4, 5, 5],
        [1, 2, 3, 4, 4],
        [0, 0, 1, 2, 2],
        [0, 0, 0, 0, 0]
    ],

    'cosecha': [
    [2, 3, 4, 4, 5],
    [1, 2, 3, 4, 4],
    [0, 1, 2, 3, 3],
    [0, 0, 0, 1, 1],
    [0, 0, 0, 0, 0]
]
}


# ==========================================
# GENERACIÓN AUTOMÁTICA DE REGLAS
# ==========================================

def generar_reglas():

    reglas = []
    contador = 1

    for nombre_etapa, matriz in MATRICES.items():

        for i, nombre_humedad in enumerate(HUMEDADES):

            for j, nombre_temperatura in enumerate(TEMPERATURAS):

                nivel_riego = matriz[i][j]
                nombre_riego = SALIDAS[nivel_riego]

                regla = ctrl.Rule(
                    humedad[nombre_humedad] &
                    temperatura[nombre_temperatura] &
                    etapa[nombre_etapa],

                    riego[nombre_riego],

                    label=f'RD-{contador:03d}'
                )

                reglas.append(regla)
                contador += 1

    return reglas


REGLAS = generar_reglas()


# ==========================================
# COMPROBACIÓN INDEPENDIENTE
# ==========================================

if __name__ == '__main__':

    print(f'Total de reglas generadas: {len(REGLAS)}')

    for regla in REGLAS:
        print(regla)
