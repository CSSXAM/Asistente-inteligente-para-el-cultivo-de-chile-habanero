
import numpy as np
import matplotlib.pyplot as plt

from .variables import (
    humedad,
    temperatura,
    etapa,
    riego,
    ETAPAS
)

from .controller import calcular_riego


# ==========================================
# FUNCIONES DE PERTENENCIA
# ==========================================

def mostrar_funciones_pertenencia():

    humedad.view()
    plt.title('Humedad aprovechable restante')
    plt.xlabel('Humedad (%)')
    plt.ylabel('Grado de pertenencia')

    temperatura.view()
    plt.title('Temperatura ambiental')
    plt.xlabel('Temperatura (°C)')
    plt.ylabel('Grado de pertenencia')

    etapa.view()
    plt.title('Etapas del cultivo')
    plt.xlabel('Etapa fenológica')
    plt.ylabel('Grado de pertenencia')

    riego.view()
    plt.title('Tiempo de riego')
    plt.xlabel('Minutos')
    plt.ylabel('Grado de pertenencia')

    plt.show()


# ==========================================
# SUPERFICIES DE CONTROL
# ==========================================

def mostrar_superficies_control():

    valores_humedad = np.linspace(0, 100, 21)
    valores_temperatura = np.linspace(0, 50, 21)

    X, Y = np.meshgrid(
        valores_humedad,
        valores_temperatura
    )

    for id_etapa, nombre_etapa in ETAPAS.items():

        print(
            f'Generando superficie: {nombre_etapa}...'
        )

        Z = np.zeros_like(X, dtype=float)

        # Evaluar cada combinación de entradas
        for i in range(X.shape[0]):

            for j in range(X.shape[1]):

                resultado = calcular_riego(
                    humedad_actual=float(X[i, j]),
                    temperatura_actual=float(Y[i, j]),
                    etapa_actual=id_etapa
                )

                Z[i, j] = resultado['minutos_riego']

        # Crear gráfica tridimensional
        figura = plt.figure(figsize=(10, 7))

        ax = figura.add_subplot(
            111,
            projection='3d'
        )

        superficie = ax.plot_surface(
            X,
            Y,
            Z,
            cmap='viridis',
            vmin=0,
            vmax=60,
            edgecolor='none',
            antialiased=True
        )

        ax.set_title(
            f'Superficie de control - {nombre_etapa.capitalize()}'
        )

        ax.set_xlabel('Humedad aprovechable (%)')
        ax.set_ylabel('Temperatura (°C)')
        ax.set_zlabel('Minutos de riego')

        ax.set_xlim(0, 100)
        ax.set_ylim(0, 50)
        ax.set_zlim(0, 60)

        ax.view_init(elev=30, azim=-135)

        figura.colorbar(
            superficie,
            ax=ax,
            shrink=0.6,
            pad=0.12,
            label='Minutos de riego'
        )

        plt.tight_layout()

        print(f'Superficie de {nombre_etapa} completada.')

    print('\nTodas las superficies fueron generadas.')

    plt.show()


# ==========================================
# MENÚ DE VISUALIZACIÓN
# ==========================================

if __name__ == '__main__':

    print('\nVISUALIZACIÓN DEL CONTROLADOR DIFUSO')
    print('1. Funciones de pertenencia')
    print('2. Superficies de control')
    print('3. Mostrar ambas')

    opcion = input('\nSelecciona una opción: ')

    if opcion == '1':

        mostrar_funciones_pertenencia()

    elif opcion == '2':

        mostrar_superficies_control()

    elif opcion == '3':

        mostrar_funciones_pertenencia()
        mostrar_superficies_control()

    else:

        print('Opción no válida.')
