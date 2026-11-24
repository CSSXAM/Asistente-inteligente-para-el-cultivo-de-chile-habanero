import matplotlib.pyplot as plt

from .variables import (
    humedad,
    temperatura,
    etapa,
    riego
)


def mostrar_funciones_pertenencia():

    humedad.view()
    plt.title('Humedad aprovechable restante')
    plt.xlabel('Humedad (%)')

    temperatura.view()
    plt.title('Temperatura ambiental')
    plt.xlabel('Temperatura (°C)')

    etapa.view()
    plt.title('Etapas del cultivo')
    plt.xlabel('Etapa fenológica')

    riego.view()
    plt.title('Tiempo de riego')
    plt.xlabel('Minutos')

    plt.show()


if __name__ == '__main__':
    mostrar_funciones_pertenencia()