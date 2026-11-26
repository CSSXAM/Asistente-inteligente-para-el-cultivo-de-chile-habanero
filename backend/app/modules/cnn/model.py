import torch
from torch import nn

from torchvision.models import (
    mobilenet_v2,
    MobileNet_V2_Weights
)


NUM_CLASES = 2

CLASES = {
    0: "enferma",
    1: "sana"
}


def crear_modelo(preentrenado=True):

    pesos = (
        MobileNet_V2_Weights.DEFAULT
        if preentrenado
        else None
    )

    modelo = mobilenet_v2(weights=pesos)

    # Congelar las capas de extracción
    # de características.

    for parametro in modelo.features.parameters():
        parametro.requires_grad = False

    # Obtener las características de entrada
    # de la capa clasificadora original.

    entradas = modelo.classifier[1].in_features

    # Sustituir la capa de 1000 clases
    # por una capa de 2 clases.

    modelo.classifier[1] = nn.Linear(
        entradas,
        NUM_CLASES
    )

    return modelo


if __name__ == "__main__":

    dispositivo = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    modelo = crear_modelo().to(dispositivo)

    modelo.eval()

    imagen = torch.rand(
        1, 3, 224, 224,
        device=dispositivo
    )

    with torch.inference_mode():
        salida = modelo(imagen)

    total_parametros = sum(
        p.numel()
        for p in modelo.parameters()
    )

    parametros_entrenables = sum(
        p.numel()
        for p in modelo.parameters()
        if p.requires_grad
    )

    print(f"Dispositivo: {dispositivo}")
    print(f"Clases: {CLASES}")
    print(f"Dimensiones de salida: {salida.shape}")
    print(f"Parámetros totales: {total_parametros:,}")
    print(
        f"Parámetros entrenables: "
        f"{parametros_entrenables:,}"
    )