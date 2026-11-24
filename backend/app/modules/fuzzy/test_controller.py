
from .controller import calcular_riego


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


if __name__ == '__main__':
    ejecutar_pruebas()
