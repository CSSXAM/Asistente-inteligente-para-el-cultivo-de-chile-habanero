
import math
import numpy as np
import skfuzzy as fuzz

from .variables import humedad, temperatura, etapa, riego, ETAPAS

from .controller import calcular_riego, normalizar_humedad
from .variables import ETAPAS
from .rules import REGLAS


CASOS_PRUEBA = [
    {
        'id': 'CP-LD-01',
        'humedad': 40,
        'temperatura': 34,
        'etapa': 5,
        'esperado': 'Muy largo',
        'rango': (45, 60)
    },
    {
        'id': 'CP-LD-02',
        'humedad': 100,
        'temperatura': 40,
        'etapa': 5,
        'esperado': 'Riego nulo',
        'rango': (0, 0)
    },
    {
        'id': 'CP-LD-03',
        'humedad': 85,
        'temperatura': 20,
        'etapa': 3,
        'esperado': 'Riego nulo',
        'rango': (0, 0)
    },
    {
        'id': 'CP-LD-04',
        'humedad': 65,
        'temperatura': 28,
        'etapa': 4,
        'esperado': 'Medio',
        'rango': (15, 35)
    },
    {
        'id': 'CP-LD-05',
        'humedad': 40,
        'temperatura': 34,
        'etapa': 1,
        'esperado': 'Medio',
        'rango': (15, 35)
    },
    {
        'id': 'CP-LD-06',
        'humedad': 110,
        'temperatura': 30,
        'etapa': 3,
        'esperado': 'Error de validación',
        'rango': None
    },
    {
        'id': 'CP-LD-07',
        'humedad': 50,
        'temperatura': 30,
        'etapa': 7,
        'esperado': 'Error de validación',
        'rango': None
    }
]


def ejecutar_pruebas():

    aprobadas = 0

    for caso in CASOS_PRUEBA:

        print('\n' + '=' * 50)
        print(f"CASO DE PRUEBA: {caso['id']}")
        print('=' * 50)

        print(f"Humedad: {caso['humedad']} %")
        print(f"Temperatura: {caso['temperatura']} °C")
        print(f"Etapa: {caso['etapa']}")
        print(f"Resultado esperado: {caso['esperado']}")

        try:

            resultado = calcular_riego(
                humedad_actual=caso['humedad'],
                temperatura_actual=caso['temperatura'],
                etapa_actual=caso['etapa']
            )

            minutos = resultado['minutos_riego']

            print(f"Etapa del cultivo: {resultado['etapa']}")
            print(f"Minutos obtenidos: {minutos}")
            print(
                f"Litros por gotero: "
                f"{resultado['litros_estimados_por_gotero']}"
            )

            if caso['rango'] is not None:

                minimo, maximo = caso['rango']
                aprobado = minimo <= minutos <= maximo

            else:
                aprobado = False

        except ValueError as error:

            print(f"Error obtenido: {error}")

            aprobado = caso['rango'] is None

        except Exception as error:

            print(f"Error inesperado: {error}")
            aprobado = False

        if aprobado:

            print('Estado: APROBADO')
            aprobadas += 1

        else:

            print('Estado: NO APROBADO')

    total = len(CASOS_PRUEBA)
    porcentaje = (aprobadas / total) * 100

    print('\n' + '=' * 50)
    print('RESUMEN GENERAL DE PRUEBAS')
    print('=' * 50)

    print(f'Total de pruebas: {total}')
    print(f'Pruebas aprobadas: {aprobadas}')
    print(f'Pruebas no aprobadas: {total - aprobadas}')
    print(f'Porcentaje de aprobación: {porcentaje:.2f} %')



# ==========================================
# VALIDACIÓN AMPLIADA DEL CONTROLADOR
# ==========================================

def probar_cobertura():

    print('\n' + '=' * 60)
    print('VALIDACIÓN DE COBERTURA')
    print('=' * 60)

    humedades = [10, 40, 65, 85, 100]
    temperaturas = [10, 22, 28, 34, 45]

    total = 0
    aprobadas = 0
    errores = []

    for etapa in ETAPAS:

        for humedad in humedades:

            for temperatura in temperaturas:

                total += 1

                try:

                    resultado = calcular_riego(
                        humedad,
                        temperatura,
                        etapa
                    )

                    minutos = resultado['minutos_riego']

                    if math.isfinite(minutos) and 0 <= minutos <= 60:
                        aprobadas += 1

                    else:
                        errores.append(
                            (humedad, temperatura, etapa, minutos)
                        )

                except Exception as error:

                    errores.append(
                        (humedad, temperatura, etapa, str(error))
                    )

    print(f'Reglas generadas: {len(REGLAS)}')
    print(f'Combinaciones evaluadas: {total}')
    print(f'Pruebas aprobadas: {aprobadas}')
    print(f'Pruebas no aprobadas: {total - aprobadas}')

    for error in errores:
        print(f'Error: {error}')


# ==========================================
# VALIDACIÓN DE VALORES LÍMITE
# ==========================================

def probar_limites():

    print('\n' + '=' * 60)
    print('VALIDACIÓN DE VALORES LÍMITE')
    print('=' * 60)

    casos = [
        (0, 0),
        (0, 50),
        (100, 0),
        (100, 50)
    ]

    total = 0
    aprobadas = 0

    for etapa in ETAPAS:

        for humedad, temperatura in casos:

            total += 1

            try:

                resultado = calcular_riego(
                    humedad,
                    temperatura,
                    etapa
                )

                minutos = resultado['minutos_riego']

                aprobado = (
                    math.isfinite(minutos)
                    and 0 <= minutos <= 60
                )

                if humedad == 100:
                    aprobado = aprobado and minutos == 0

                if aprobado:
                    aprobadas += 1

                estado = 'APROBADO' if aprobado else 'NO APROBADO'

                print(
                    f'{ETAPAS[etapa]} | '
                    f'H: {humedad}% | '
                    f'T: {temperatura}°C | '
                    f'Riego: {minutos} min | '
                    f'{estado}'
                )

            except Exception as error:
                print(f'Error: {error}')

    print(f'\nPruebas aprobadas: {aprobadas}/{total}')


# ==========================================
# VALIDACIÓN DE NORMALIZACIÓN
# ==========================================

def probar_normalizacion():

    print('\n' + '=' * 60)
    print('VALIDACIÓN DE NORMALIZACIÓN DE HUMEDAD')
    print('=' * 60)

    capacidad_campo = 31.5
    punto_marchitez = 20

    casos = [
        (20, 0),
        (25.75, 50),
        (31.5, 100),
        (15, 0),
        (40, 100)
    ]

    aprobadas = 0

    for humedad_suelo, esperado in casos:

        obtenido = normalizar_humedad(
            humedad_suelo,
            capacidad_campo,
            punto_marchitez
        )

        aprobado = math.isclose(
            obtenido,
            esperado,
            abs_tol=0.01
        )

        if aprobado:
            aprobadas += 1

        estado = 'APROBADO' if aprobado else 'NO APROBADO'

        print(
            f'Humedad del suelo: {humedad_suelo}% | '
            f'Esperado: {esperado}% | '
            f'Obtenido: {obtenido:.2f}% | '
            f'{estado}'
        )

    print(f'\nPruebas aprobadas: {aprobadas}/{len(casos)}')


# ==========================================
# VALIDACIÓN DE COHERENCIA
# ==========================================

def probar_coherencia():

    print('\n' + '=' * 60)
    print('VALIDACIÓN DE COHERENCIA DEL RIEGO')
    print('=' * 60)

    humedades = range(0, 101, 5)
    temperaturas = range(0, 51, 5)

    incidencias_humedad = []
    incidencias_temperatura = []

    # Margen numérico de comparación en minutos
    tolerancia = 0.01

    for etapa in ETAPAS:

        # Calcular y almacenar resultados
        resultados = {}

        for humedad in humedades:

            for temperatura in temperaturas:

                resultado = calcular_riego(
                    humedad,
                    temperatura,
                    etapa
                )

                resultados[(humedad, temperatura)] = (
                    resultado['minutos_riego']
                )

        # Al aumentar la humedad,
        # el riego no debería aumentar.

        for temperatura in temperaturas:

            for humedad in range(0, 100, 5):

                anterior = resultados[(humedad, temperatura)]
                actual = resultados[(humedad + 5, temperatura)]

                if actual > anterior + tolerancia:

                    incidencias_humedad.append(
                        f'{ETAPAS[etapa]} | '
                        f'T: {temperatura}°C | '
                        f'H: {humedad}% -> {humedad + 5}% | '
                        f'Riego: {anterior} -> {actual} min'
                    )

        # Al aumentar la temperatura,
        # el riego no debería disminuir.

        for humedad in humedades:

            for temperatura in range(0, 50, 5):

                anterior = resultados[(humedad, temperatura)]
                actual = resultados[(humedad, temperatura + 5)]

                if actual < anterior - tolerancia:

                    incidencias_temperatura.append(
                        f'{ETAPAS[etapa]} | '
                        f'H: {humedad}% | '
                        f'T: {temperatura} -> {temperatura + 5}°C | '
                        f'Riego: {anterior} -> {actual} min'
                    )

    print('\nIncidencias relacionadas con la humedad:')
    print(f'Total: {len(incidencias_humedad)}')

    for incidencia in incidencias_humedad:
        print(incidencia)

    print('\nIncidencias relacionadas con la temperatura:')
    print(f'Total: {len(incidencias_temperatura)}')

    for incidencia in incidencias_temperatura:
        print(incidencia)

    if not incidencias_humedad and not incidencias_temperatura:

        print('\nEstado: APROBADO')

    else:

        print('\nEstado: REQUIERE REVISIÓN')


# ==========================================
# COMPARACIÓN ENTRE ETAPAS FENOLÓGICAS
# ==========================================

def comparar_etapas():

    print('\n' + '=' * 60)
    print('COMPARACIÓN ENTRE ETAPAS FENOLÓGICAS')
    print('=' * 60)

    escenarios = [
        (40, 34),
        (65, 28),
        (85, 22)
    ]

    for humedad, temperatura in escenarios:

        print(
            f'\nHumedad: {humedad}% | '
            f'Temperatura: {temperatura}°C'
        )

        print('-' * 45)

        for etapa in ETAPAS:

            resultado = calcular_riego(
                humedad,
                temperatura,
                etapa
            )

            print(
                f'{ETAPAS[etapa]:15} | '
                f'{resultado["minutos_riego"]:6.2f} min'
            )


# ==========================================
# VALIDACIÓN DE FUNCIONES DE PERTENENCIA
# ==========================================

def probar_funciones_pertenencia():

    print('\n' + '=' * 60)
    print('VALIDACIÓN DE FUNCIONES DE PERTENENCIA')
    print('=' * 60)

    total = 0
    aprobadas = 0

    def verificar(descripcion, condicion):

        nonlocal total, aprobadas

        total += 1

        if condicion:
            aprobadas += 1
            estado = 'APROBADO'
        else:
            estado = 'NO APROBADO'

        print(f'{descripcion} | {estado}')


    # ======================================
    # 1. RANGO DE LOS GRADOS DE PERTENENCIA
    # ======================================

    print('\n1. RANGO DE PERTENENCIA\n')

    variables = [humedad, temperatura, etapa, riego]

    for variable in variables:

        for nombre, termino in variable.terms.items():

            valores = termino.mf

            valido = (
                np.all(np.isfinite(valores))
                and np.all(valores >= 0)
                and np.all(valores <= 1)
            )

            verificar(
                f'{variable.label} - {nombre}',
                valido
            )


    # ======================================
    # 2. COBERTURA DEL UNIVERSO DE DISCURSO
    # ======================================

    print('\n2. COBERTURA DE LOS UNIVERSOS\n')

    for variable in variables:

        funciones = [
            termino.mf
            for termino in variable.terms.values()
        ]

        cobertura = np.max(funciones, axis=0)

        verificar(
            f'Cobertura de {variable.label}',
            np.all(cobertura > 0)
        )


    # ======================================
    # 3. VALORES MATEMÁTICOS ESPERADOS
    # ======================================

    print('\n3. GRADOS DE PERTENENCIA ESPERADOS\n')

    casos = [

        # Humedad aprovechable
        (humedad, 'muy_seca', 10, 1),
        (humedad, 'muy_seca', 25, 2/3),
        (humedad, 'seca', 20, 0),
        (humedad, 'seca', 30, 0.5),
        (humedad, 'seca', 40, 1),
        (humedad, 'seca', 50, 0.5),
        (humedad, 'seca', 60, 0),
        (humedad, 'moderada', 55, 0.5),
        (humedad, 'moderada', 65, 1),
        (humedad, 'optima', 75, 0.5),
        (humedad, 'optima', 85, 1),
        (humedad, 'muy_humeda', 92.5, 0.5),
        (humedad, 'muy_humeda', 100, 1),

        # Temperatura ambiental
        (temperatura, 'fria', 10, 1),
        (temperatura, 'fria', 18.5, 0.5),
        (temperatura, 'templada', 22, 1),
        (temperatura, 'templada', 24, 0.5),
        (temperatura, 'optima', 24.5, 0.5),
        (temperatura, 'optima', 28, 1),
        (temperatura, 'caliente', 32, 0.5),
        (temperatura, 'caliente', 34, 1),
        (temperatura, 'muy_caliente', 37, 0.5),
        (temperatura, 'muy_caliente', 45, 1),

        # Tiempo de riego
        (riego, 'nulo', 0, 1),
        (riego, 'nulo', 2, 0.5),
        (riego, 'muy_corto', 5, 1),
        (riego, 'corto', 8.5, 0.5),
        (riego, 'corto', 12, 1),
        (riego, 'medio', 20, 0.5),
        (riego, 'medio', 25, 1),
        (riego, 'largo', 35, 0.5),
        (riego, 'largo', 40, 1),
        (riego, 'muy_largo', 50, 0.5),
        (riego, 'muy_largo', 60, 1)
    ]

    for variable, nombre, valor, esperado in casos:

        obtenido = fuzz.interp_membership(
            variable.universe,
            variable[nombre].mf,
            valor
        )

        verificar(
            f'{variable.label}[{nombre}] | '
            f'Entrada: {valor} | '
            f'Esperado: {esperado:.4f} | '
            f'Obtenido: {obtenido:.4f}',
            np.isclose(
                obtenido,
                esperado,
                atol=0.0001,
                rtol=0
            )
        )


    # ======================================
    # 4. SUPERPOSICIÓN DE CONJUNTOS DIFUSOS
    # ======================================

    print('\n4. SUPERPOSICIÓN DE CONJUNTOS\n')

    for variable in [humedad, temperatura, riego]:

        nombres = list(variable.terms.keys())

        for i in range(len(nombres) - 1):

            primero = nombres[i]
            segundo = nombres[i + 1]

            superposicion = np.minimum(
                variable[primero].mf,
                variable[segundo].mf
            )

            verificar(
                f'{variable.label}: '
                f'{primero} / {segundo}',
                np.any(superposicion > 0)
            )


    # ======================================
    # 5. ETAPAS FENOLÓGICAS
    # ======================================

    print('\n5. PERTENENCIA DE ETAPAS FENOLÓGICAS\n')

    for id_etapa, nombre_etapa in ETAPAS.items():

        for nombre_conjunto in ETAPAS.values():

            esperado = (
                1.0 if nombre_etapa == nombre_conjunto
                else 0.0
            )

            obtenido = fuzz.interp_membership(
                etapa.universe,
                etapa[nombre_conjunto].mf,
                id_etapa
            )

            verificar(
                f'Etapa: {nombre_etapa} | '
                f'Conjunto: {nombre_conjunto} | '
                f'Esperado: {esperado} | '
                f'Obtenido: {obtenido}',
                np.isclose(obtenido, esperado)
            )


    # ======================================
    # RESUMEN GENERAL
    # ======================================

    print('\n' + '=' * 60)
    print('RESUMEN DE FUNCIONES DE PERTENENCIA')
    print('=' * 60)

    print(f'Total de pruebas: {total}')
    print(f'Pruebas aprobadas: {aprobadas}')
    print(f'Pruebas no aprobadas: {total - aprobadas}')

    porcentaje = aprobadas / total * 100

    print(f'Porcentaje de aprobación: {porcentaje:.2f}%')

    if aprobadas == total:
        print('Estado: APROBADO')
    else:
        print('Estado: REQUIERE REVISIÓN')


if __name__ == '__main__':

    probar_funciones_pertenencia()

    ejecutar_pruebas()

    probar_cobertura()

    probar_limites()

    probar_normalizacion()

    probar_coherencia()

    comparar_etapas()
