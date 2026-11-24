import math

import skfuzzy as fuzz
from skfuzzy import control as ctrl

from .variables import humedad, temperatura, ETAPAS
from .rules import REGLAS, MATRICES, HUMEDADES, TEMPERATURAS


# ==========================================
# SISTEMA DE CONTROL DIFUSO
# ==========================================

SISTEMA_RIEGO = ctrl.ControlSystem(REGLAS)

CAUDAL_REFERENCIA = 2.0


# ==========================================
# VALIDACIÓN DE ENTRADAS
# ==========================================

def validar_entradas(
    humedad_actual,
    temperatura_actual,
    etapa_actual
):

    if not math.isfinite(humedad_actual):
        raise ValueError('La humedad debe ser un valor finito.')

    if not math.isfinite(temperatura_actual):
        raise ValueError('La temperatura debe ser un valor finito.')

    if not 0 <= humedad_actual <= 100:
        raise ValueError(
            'La humedad debe estar entre 0 y 100 %.'
        )

    if not 0 <= temperatura_actual <= 50:
        raise ValueError(
            'La temperatura debe estar entre 0 y 50 °C.'
        )

    if type(etapa_actual) is not int or etapa_actual not in ETAPAS:
        raise ValueError(
            'La etapa debe ser un número entero del 1 al 6.'
        )


# ==========================================
# NORMALIZACIÓN DE HUMEDAD
# ==========================================

def normalizar_humedad(
    humedad_suelo,
    capacidad_campo,
    punto_marchitez
):

    valores = [
        humedad_suelo,
        capacidad_campo,
        punto_marchitez
    ]

    if not all(math.isfinite(v) for v in valores):
        raise ValueError('Los valores deben ser finitos.')

    if not 0 <= humedad_suelo <= 100:
        raise ValueError('Humedad del suelo inválida.')

    if not 0 <= punto_marchitez < capacidad_campo <= 100:
        raise ValueError(
            'La capacidad de campo debe ser mayor '
            'que el punto de marchitez permanente.'
        )

    humedad_normalizada = (
        (humedad_suelo - punto_marchitez) /
        (capacidad_campo - punto_marchitez)
    ) * 100

    return max(0, min(100, humedad_normalizada))


# ==========================================
# COMPROBACIÓN DE RIEGO NULO
# ==========================================

def requiere_riego(
    humedad_actual,
    temperatura_actual,
    etapa_actual
):

    matriz = MATRICES[ETAPAS[etapa_actual]]

    for i, nombre_humedad in enumerate(HUMEDADES):

        pertenencia_humedad = fuzz.interp_membership(
            humedad.universe,
            humedad[nombre_humedad].mf,
            humedad_actual
        )

        for j, nombre_temperatura in enumerate(TEMPERATURAS):

            pertenencia_temperatura = fuzz.interp_membership(
                temperatura.universe,
                temperatura[nombre_temperatura].mf,
                temperatura_actual
            )

            activacion = min(
                pertenencia_humedad,
                pertenencia_temperatura
            )

            if activacion > 0 and matriz[i][j] != 0:
                return True

    return False


# ==========================================
# CÁLCULO DE RIEGO
# ==========================================

def calcular_riego(
    humedad_actual,
    temperatura_actual,
    etapa_actual
):

    validar_entradas(
        humedad_actual,
        temperatura_actual,
        etapa_actual
    )

    # Evitar riego cuando se alcanza la capacidad de campo
    if humedad_actual >= 100:

        minutos = 0.0

    # Evitar residuos del centroide cuando
    # todas las reglas activadas indican riego nulo
    elif not requiere_riego(
        humedad_actual,
        temperatura_actual,
        etapa_actual
    ):

        minutos = 0.0

    else:

        simulacion = ctrl.ControlSystemSimulation(
            SISTEMA_RIEGO
        )

        simulacion.input['humedad'] = humedad_actual
        simulacion.input['temperatura'] = temperatura_actual
        simulacion.input['etapa'] = etapa_actual

        simulacion.compute()

        minutos = float(simulacion.output['riego'])

    minutos = round(minutos, 2)

    litros = (minutos / 60) * CAUDAL_REFERENCIA

    return {
        'humedad': humedad_actual,
        'temperatura': temperatura_actual,
        'etapa': ETAPAS[etapa_actual],
        'minutos_riego': minutos,
        'caudal_litros_hora': CAUDAL_REFERENCIA,
        'litros_estimados_por_gotero': round(litros, 3)
    }


# ==========================================
# PRUEBA INDEPENDIENTE
# ==========================================

if __name__ == '__main__':

    resultado = calcular_riego(
        humedad_actual=40,
        temperatura_actual=34,
        etapa_actual=5
    )

    for clave, valor in resultado.items():
        print(f'{clave}: {valor}')
