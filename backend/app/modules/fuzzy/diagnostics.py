
import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt

from skfuzzy import control as ctrl

from collections import Counter
from statistics import mean, median

from .variables import (
    humedad,
    temperatura,
    etapa,
    riego,
    ETAPAS
)

from .rules import (
    MATRICES,
    HUMEDADES,
    TEMPERATURAS,
    SALIDAS,
    REGLAS
)

from .controller import (
    SISTEMA_RIEGO,
    calcular_riego,
    validar_entradas,
    CAUDAL_REFERENCIA
)


# ==========================================
# OBTENER GRADOS DE PERTENENCIA
# ==========================================

def obtener_pertenencias(variable, valor):

    pertenencias = {}

    for nombre, termino in variable.terms.items():

        grado = fuzz.interp_membership(
            variable.universe,
            termino.mf,
            valor
        )

        pertenencias[nombre] = float(grado)

    return pertenencias


# ==========================================
# DIAGNÓSTICO DE UN ESCENARIO
# ==========================================

def diagnosticar_escenario(
    humedad_actual,
    temperatura_actual,
    etapa_actual
):

    validar_entradas(
        humedad_actual,
        temperatura_actual,
        etapa_actual
    )

    nombre_etapa = ETAPAS[etapa_actual]

    print('\n' + '=' * 65)
    print('DIAGNÓSTICO DEL CONTROLADOR DIFUSO')
    print('=' * 65)

    print(f'Humedad: {humedad_actual}%')
    print(f'Temperatura: {temperatura_actual}°C')
    print(f'Etapa: {nombre_etapa}')


    # ======================================
    # 1. FUZZIFICACIÓN
    # ======================================

    pertenencias_humedad = obtener_pertenencias(
        humedad,
        humedad_actual
    )

    pertenencias_temperatura = obtener_pertenencias(
        temperatura,
        temperatura_actual
    )

    pertenencias_etapa = obtener_pertenencias(
        etapa,
        etapa_actual
    )

    print('\n1. PERTENENCIA DE HUMEDAD')

    for nombre, grado in pertenencias_humedad.items():

        print(f'{nombre:15} | {grado:.4f}')

    print('\n2. PERTENENCIA DE TEMPERATURA')

    for nombre, grado in pertenencias_temperatura.items():

        print(f'{nombre:15} | {grado:.4f}')

    print('\n3. PERTENENCIA DE ETAPA')

    for nombre, grado in pertenencias_etapa.items():

        print(f'{nombre:15} | {grado:.4f}')


    # ======================================
    # 2. ACTIVACIÓN DE REGLAS
    # ======================================

    simulacion = ctrl.ControlSystemSimulation(
        SISTEMA_RIEGO
    )

    simulacion.input['humedad'] = humedad_actual
    simulacion.input['temperatura'] = temperatura_actual
    simulacion.input['etapa'] = etapa_actual

    simulacion.compute()

    activaciones = {
        nombre: 0.0
        for nombre in SALIDAS.values()
    }

    print('\n4. REGLAS ACTIVADAS')

    for regla in REGLAS:

        intensidad = float(
            regla.aggregate_firing[simulacion]
        )

        if intensidad <= 0:
            continue

        for consecuente in regla.consequent:

            nombre_salida = consecuente.term.label

            activacion = float(
                consecuente.activation[simulacion]
            )

            activaciones[nombre_salida] = max(
                activaciones[nombre_salida],
                activacion
            )

            print('\n' + '-' * 45)
            print(f'Regla: {regla.label}')
            print(f'Condición: {regla.antecedent}')
            print(f'Salida: {nombre_salida}')
            print(f'Intensidad: {intensidad:.4f}')


    # ======================================
    # 3. AGREGACIÓN DE CONSECUENTES
    # ======================================

    print('\n5. ACTIVACIÓN FINAL DE LAS SALIDAS')

    for nombre, intensidad in activaciones.items():

        print(f'{nombre:15} | {intensidad:.4f}')

    # Incorporar los puntos de corte al universo
    # para representar mejor las funciones recortadas.

    puntos = [riego.universe]

    for nombre, intensidad in activaciones.items():

        if intensidad > 0:

            intersecciones = fuzz.interp_universe(
                riego.universe,
                riego[nombre].mf,
                intensidad
            )

            puntos.append(intersecciones)

    universo = np.unique(
        np.concatenate(puntos)
    )

    agregacion = np.zeros_like(
        universo,
        dtype=float
    )

    conjuntos_recortados = {}

    for nombre, intensidad in activaciones.items():

        funcion = fuzz.interp_membership(
            riego.universe,
            riego[nombre].mf,
            universo
        )

        recortada = np.minimum(
            intensidad,
            funcion
        )

        conjuntos_recortados[nombre] = recortada

        agregacion = np.maximum(
            agregacion,
            recortada
        )


    # ======================================
    # 4. DESFUZZIFICACIÓN
    # ======================================

    centroide = fuzz.defuzz(
        universo,
        agregacion,
        'centroid'
    )

    centroide_sistema = float(
        simulacion.output['riego']
    )

    resultado = calcular_riego(
        humedad_actual,
        temperatura_actual,
        etapa_actual
    )

    print('\n6. RESULTADOS DE DESFUZZIFICACIÓN')

    print(
        f'Centroide reconstruido: '
        f'{centroide:.4f} min'
    )

    print(
        f'Centroide Scikit-Fuzzy: '
        f'{centroide_sistema:.4f} min'
    )

    print(
        f'Recomendación final: '
        f'{resultado["minutos_riego"]:.2f} min'
    )

    print(
        f'Litros estimados por gotero: '
        f'{resultado["litros_estimados_por_gotero"]}'
    )

    return {
        'humedad': humedad_actual,
        'temperatura': temperatura_actual,
        'etapa': nombre_etapa,
        'activaciones': activaciones,
        'universo': universo,
        'agregacion': agregacion,
        'conjuntos': conjuntos_recortados,
        'centroide': centroide_sistema,
        'minutos': resultado['minutos_riego']
    }


# ==========================================
# VISUALIZACIÓN DEL DIAGNÓSTICO
# ==========================================

def graficar_diagnostico(datos):

    figura, ax = plt.subplots(
        figsize=(10, 6)
    )

    universo = datos['universo']

    # Funciones originales

    for nombre, termino in riego.terms.items():

        ax.plot(
            riego.universe,
            termino.mf,
            linestyle='--',
            alpha=0.35,
            label=nombre
        )

    # Funciones activadas y recortadas

    for nombre, conjunto in datos['conjuntos'].items():

        if datos['activaciones'][nombre] > 0:

            ax.fill_between(
                universo,
                0,
                conjunto,
                alpha=0.25
            )

    # Agregación final

    ax.plot(
        universo,
        datos['agregacion'],
        color='black',
        linewidth=2,
        label='Agregación final'
    )

    # Centroide

    ax.axvline(
        datos['centroide'],
        color='red',
        linestyle='-',
        linewidth=2,
        label=(
            f'Centroide: '
            f'{datos["centroide"]:.2f} min'
        )
    )

    ax.set_title(
        f'Diagnóstico - {datos["etapa"].capitalize()}\n'
        f'Humedad: {datos["humedad"]}% | '
        f'Temperatura: {datos["temperatura"]}°C'
    )

    ax.set_xlabel('Minutos de riego')
    ax.set_ylabel('Grado de pertenencia')

    ax.set_xlim(0, 60)
    ax.set_ylim(0, 1.05)

    ax.grid(alpha=0.2)
    ax.legend()

    plt.tight_layout()


# ==========================================
# COMPARACIÓN DE ESCENARIOS
# ==========================================

def comparar_escenarios(escenarios):

    resultados = []

    for humedad_actual, temperatura_actual, etapa_actual in escenarios:

        datos = diagnosticar_escenario(
            humedad_actual,
            temperatura_actual,
            etapa_actual
        )

        resultados.append(datos)

        graficar_diagnostico(datos)

    print('\n' + '=' * 65)
    print('RESUMEN COMPARATIVO')
    print('=' * 65)

    for datos in resultados:

        print(
            f'{datos["etapa"]:15} | '
            f'H: {datos["humedad"]}% | '
            f'T: {datos["temperatura"]}°C | '
            f'Riego: {datos["minutos"]:.2f} min'
        )

    plt.show()


# ==========================================
# CLASIFICACIÓN DE INCIDENCIAS
# ==========================================

def clasificar_magnitud(diferencia):

    if diferencia <= 0.10:
        return 'Muy pequeña'

    elif diferencia <= 0.50:
        return 'Pequeña'

    elif diferencia <= 1.00:
        return 'Moderada'

    elif diferencia <= 2.00:
        return 'Considerable'

    else:
        return 'Alta'


# ==========================================
# REGISTRO DE INCIDENCIAS
# ==========================================

def registrar_incidencia(
    tipo,
    etapa,
    humedad_anterior,
    humedad_actual,
    temperatura_anterior,
    temperatura_actual,
    riego_anterior,
    riego_actual
):

    diferencia = round(
        abs(riego_actual - riego_anterior),
        2
    )

    return {
        'tipo': tipo,
        'etapa': etapa,
        'humedad_anterior': humedad_anterior,
        'humedad_actual': humedad_actual,
        'temperatura_anterior': temperatura_anterior,
        'temperatura_actual': temperatura_actual,
        'riego_anterior': riego_anterior,
        'riego_actual': riego_actual,
        'diferencia_minutos': diferencia,
        'diferencia_segundos': diferencia * 60,
        'diferencia_mililitros': (
            diferencia / 60
        ) * CAUDAL_REFERENCIA * 1000,
        'magnitud': clasificar_magnitud(diferencia)
    }


# ==========================================
# ANÁLISIS ESTADÍSTICO DE INCIDENCIAS
# ==========================================

def analizar_incidencias():

    print('\n' + '=' * 65)
    print('ANÁLISIS ESTADÍSTICO DE INCIDENCIAS')
    print('=' * 65)

    humedades = range(0, 101, 5)
    temperaturas = range(0, 51, 5)

    tolerancia = 0.01

    incidencias = []
    total_comparaciones = 0

    for id_etapa, nombre_etapa in ETAPAS.items():

        print(f'\nAnalizando etapa: {nombre_etapa}...')

        resultados = {}

        # Calcular resultados por etapa

        for h in humedades:

            for t in temperaturas:

                resultado = calcular_riego(
                    h,
                    t,
                    id_etapa
                )

                resultados[(h, t)] = (
                    resultado['minutos_riego']
                )


        # ==================================
        # INCIDENCIAS DE HUMEDAD
        # ==================================

        for t in temperaturas:

            for h in range(0, 100, 5):

                anterior = resultados[(h, t)]
                actual = resultados[(h + 5, t)]

                total_comparaciones += 1

                if actual > anterior + tolerancia:

                    incidencia = registrar_incidencia(
                        'Humedad',
                        nombre_etapa,
                        h,
                        h + 5,
                        t,
                        t,
                        anterior,
                        actual
                    )

                    incidencias.append(incidencia)


        # ==================================
        # INCIDENCIAS DE TEMPERATURA
        # ==================================

        for h in humedades:

            for t in range(0, 50, 5):

                anterior = resultados[(h, t)]
                actual = resultados[(h, t + 5)]

                total_comparaciones += 1

                if actual < anterior - tolerancia:

                    incidencia = registrar_incidencia(
                        'Temperatura',
                        nombre_etapa,
                        h,
                        h,
                        t,
                        t + 5,
                        anterior,
                        actual
                    )

                    incidencias.append(incidencia)

        print(f'Etapa {nombre_etapa} completada.')


    # ======================================
    # RESUMEN GENERAL
    # ======================================

    total_incidencias = len(incidencias)

    coherentes = (
        total_comparaciones - total_incidencias
    )

    porcentaje = (
        coherentes / total_comparaciones
    ) * 100

    print('\n' + '=' * 65)
    print('RESUMEN GENERAL')
    print('=' * 65)

    print(f'Comparaciones: {total_comparaciones}')
    print(f'Comparaciones coherentes: {coherentes}')
    print(f'Incidencias: {total_incidencias}')
    print(f'Coherencia general: {porcentaje:.2f}%')

    if not incidencias:

        print('No se detectaron incidencias.')
        return incidencias


    # ======================================
    # INCIDENCIAS POR TIPO
    # ======================================

    print('\nINCIDENCIAS POR TIPO')

    por_tipo = Counter(
        i['tipo'] for i in incidencias
    )

    for tipo, cantidad in por_tipo.items():

        print(f'{tipo:15} | {cantidad}')


    # ======================================
    # INCIDENCIAS POR ETAPA
    # ======================================

    print('\nINCIDENCIAS POR ETAPA')

    por_etapa = Counter(
        i['etapa'] for i in incidencias
    )

    for nombre in ETAPAS.values():

        print(f'{nombre:15} | {por_etapa[nombre]}')


    # ======================================
    # ESTADÍSTICAS DE LAS DESVIACIONES
    # ======================================

    diferencias = [
        i['diferencia_minutos']
        for i in incidencias
    ]

    estadisticas = {
        'Mínima': min(diferencias),
        'Máxima': max(diferencias),
        'Promedio': mean(diferencias),
        'Mediana': median(diferencias)
    }

    print('\nESTADÍSTICAS DE LAS DESVIACIONES')

    for nombre, valor in estadisticas.items():

        segundos = valor * 60

        mililitros = (
            valor / 60
        ) * CAUDAL_REFERENCIA * 1000

        print(
            f'{nombre:10} | '
            f'{valor:.4f} min | '
            f'{segundos:.2f} s | '
            f'{mililitros:.2f} ml'
        )


    # ======================================
    # DISTRIBUCIÓN POR MAGNITUD
    # ======================================

    categorias = [
        'Muy pequeña',
        'Pequeña',
        'Moderada',
        'Considerable',
        'Alta'
    ]

    por_magnitud = Counter(
        i['magnitud'] for i in incidencias
    )

    print('\nDISTRIBUCIÓN POR MAGNITUD')

    for categoria in categorias:

        cantidad = por_magnitud[categoria]

        porcentaje_categoria = (
            cantidad / total_incidencias
        ) * 100

        print(
            f'{categoria:15} | '
            f'{cantidad:3} | '
            f'{porcentaje_categoria:.2f}%'
        )


    # ======================================
    # INCIDENCIAS DE MAYOR MAGNITUD
    # ======================================

    ordenadas = sorted(
        incidencias,
        key=lambda i: i['diferencia_minutos'],
        reverse=True
    )

    print('\n' + '=' * 65)
    print('10 INCIDENCIAS DE MAYOR MAGNITUD')
    print('=' * 65)

    for posicion, i in enumerate(ordenadas[:10], 1):

        print(f'\nIncidencia #{posicion}')
        print(f'Tipo: {i["tipo"]}')
        print(f'Etapa: {i["etapa"]}')

        print(
            f'Humedad: '
            f'{i["humedad_anterior"]}% -> '
            f'{i["humedad_actual"]}%'
        )

        print(
            f'Temperatura: '
            f'{i["temperatura_anterior"]}°C -> '
            f'{i["temperatura_actual"]}°C'
        )

        print(
            f'Riego: '
            f'{i["riego_anterior"]} -> '
            f'{i["riego_actual"]} min'
        )

        print(
            f'Diferencia: '
            f'{i["diferencia_minutos"]:.2f} min'
        )

        print(
            f'Equivalencia: '
            f'{i["diferencia_segundos"]:.2f} s | '
            f'{i["diferencia_mililitros"]:.2f} ml'
        )

        print(f'Magnitud: {i["magnitud"]}')


    # ======================================
    # GRÁFICA DE INCIDENCIAS POR ETAPA
    # ======================================

    nombres_etapas = list(ETAPAS.values())

    plt.figure(figsize=(10, 6))

    barras = plt.bar(
        nombres_etapas,
        [por_etapa[n] for n in nombres_etapas],
        color='steelblue'
    )

    plt.bar_label(barras, padding=3)

    plt.title('Incidencias por etapa fenológica')
    plt.xlabel('Etapa del cultivo')
    plt.ylabel('Cantidad de incidencias')

    plt.grid(axis='y', alpha=0.2)
    plt.tight_layout()


    # ======================================
    # GRÁFICA DE MAGNITUD
    # ======================================

    plt.figure(figsize=(10, 6))

    barras = plt.bar(
        categorias,
        [por_magnitud[c] for c in categorias],
        color=[
            '#22a06b',
            '#84cc16',
            '#eab308',
            '#f97316',
            '#ef4444'
        ]
    )

    plt.bar_label(barras, padding=3)

    plt.title('Distribución de incidencias por magnitud')
    plt.xlabel('Magnitud de la desviación')
    plt.ylabel('Cantidad de incidencias')

    plt.grid(axis='y', alpha=0.2)
    plt.tight_layout()


    # ======================================
    # HISTOGRAMA DE DESVIACIONES
    # ======================================

    plt.figure(figsize=(10, 6))

    plt.hist(
        diferencias,
        bins=15,
        color='steelblue',
        edgecolor='black'
    )

    plt.axvline(
        mean(diferencias),
        color='red',
        linestyle='--',
        label=f'Promedio: {mean(diferencias):.3f} min'
    )

    plt.axvline(
        median(diferencias),
        color='orange',
        linestyle='--',
        label=f'Mediana: {median(diferencias):.3f} min'
    )

    plt.title('Histograma de las desviaciones')
    plt.xlabel('Diferencia absoluta en minutos')
    plt.ylabel('Frecuencia')

    plt.legend()
    plt.grid(axis='y', alpha=0.2)
    plt.tight_layout()

    plt.show()

    return incidencias


# ==========================================
# EJECUCIÓN PRINCIPAL
# ==========================================

if __name__ == '__main__':

    print('\nDIAGNÓSTICO DEL CONTROLADOR DIFUSO')
    print('1. Diagnóstico de escenarios específicos')
    print('2. Análisis estadístico de incidencias')
    print('3. Ejecutar ambos diagnósticos')

    opcion = input('\nSelecciona una opción: ')

    escenarios = [
        (30, 20, 6),
        (35, 20, 6),
        (10, 30, 5),
        (10, 35, 5)
    ]

    if opcion == '1':

        comparar_escenarios(escenarios)

    elif opcion == '2':

        analizar_incidencias()

    elif opcion == '3':

        comparar_escenarios(escenarios)
        analizar_incidencias()

    else:

        print('Opción no válida.')