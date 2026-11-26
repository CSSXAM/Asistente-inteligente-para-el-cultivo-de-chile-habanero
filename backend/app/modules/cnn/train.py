import json
import random
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn, optim
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder

from .model import crear_modelo
from .preprocessing import (
    obtener_transformaciones_entrenamiento,
    obtener_transformaciones_evaluacion
)


# Configuración del entrenamiento

SEMILLA = 42
EPOCAS = 10
BATCH_SIZE = 32
LEARNING_RATE = 0.001

RAIZ_PROYECTO = Path(__file__).resolve().parents[4]
DATASET = RAIZ_PROYECTO / "datasets" / "cnn"

CARPETA_MODELOS = Path(__file__).resolve().parent / "models"

RUTA_MODELO = CARPETA_MODELOS / "clasificador.pth"
RUTA_HISTORIAL = CARPETA_MODELOS / "historial_entrenamiento.json"

DISPOSITIVO = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# Configuración de semillas

def configurar_semilla():
    random.seed(SEMILLA)
    np.random.seed(SEMILLA)
    torch.manual_seed(SEMILLA)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEMILLA)


# Carga de los conjuntos de datos

def cargar_datos():

    datos_train = ImageFolder(
        root=DATASET / "train",
        transform=obtener_transformaciones_entrenamiento()
    )

    datos_val = ImageFolder(
        root=DATASET / "validation",
        transform=obtener_transformaciones_evaluacion()
    )

    clases_esperadas = {
        "enferma": 0,
        "sana": 1
    }

    if datos_train.class_to_idx != clases_esperadas:
        raise ValueError(
            "Las clases de entrenamiento no son correctas."
        )

    if datos_val.class_to_idx != clases_esperadas:
        raise ValueError(
            "Las clases de validación no son correctas."
        )

    generador = torch.Generator()
    generador.manual_seed(SEMILLA)

    loader_train = DataLoader(
        datos_train,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
        pin_memory=DISPOSITIVO.type == "cuda",
        generator=generador
    )

    loader_val = DataLoader(
        datos_val,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
        pin_memory=DISPOSITIVO.type == "cuda"
    )

    print(f"Imágenes de entrenamiento: {len(datos_train)}")
    print(f"Imágenes de validación: {len(datos_val)}")
    print(f"Clases: {datos_train.class_to_idx}")

    return loader_train, loader_val, datos_train.class_to_idx


# Entrenamiento de una época

def entrenar_epoca(modelo, loader, criterio, optimizador):

    modelo.train()

    # Mantener congelado el extractor de características
    modelo.features.eval()

    perdida_total = 0.0
    aciertos = 0
    total = 0

    for imagenes, etiquetas in loader:

        imagenes = imagenes.to(DISPOSITIVO)
        etiquetas = etiquetas.to(DISPOSITIVO)

        optimizador.zero_grad()

        salidas = modelo(imagenes)

        perdida = criterio(salidas, etiquetas)

        perdida.backward()

        optimizador.step()

        predicciones = salidas.argmax(dim=1)

        perdida_total += perdida.item() * etiquetas.size(0)

        aciertos += (
            predicciones == etiquetas
        ).sum().item()

        total += etiquetas.size(0)

    return perdida_total / total, aciertos / total


# Validación de una época

def validar_epoca(modelo, loader, criterio):

    modelo.eval()

    perdida_total = 0.0
    aciertos = 0
    total = 0

    with torch.inference_mode():

        for imagenes, etiquetas in loader:

            imagenes = imagenes.to(DISPOSITIVO)
            etiquetas = etiquetas.to(DISPOSITIVO)

            salidas = modelo(imagenes)

            perdida = criterio(salidas, etiquetas)

            predicciones = salidas.argmax(dim=1)

            perdida_total += perdida.item() * etiquetas.size(0)

            aciertos += (
                predicciones == etiquetas
            ).sum().item()

            total += etiquetas.size(0)

    return perdida_total / total, aciertos / total


# Función principal de entrenamiento

def entrenar():

    configurar_semilla()

    CARPETA_MODELOS.mkdir(
        parents=True,
        exist_ok=True
    )

    print("=" * 60)
    print("ENTRENAMIENTO CNN - MOBILENETV2")
    print("=" * 60)

    print(f"Dispositivo: {DISPOSITIVO}")

    if DISPOSITIVO.type == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    loader_train, loader_val, clases = cargar_datos()

    modelo = crear_modelo(
        preentrenado=True
    ).to(DISPOSITIVO)

    criterio = nn.CrossEntropyLoss()

    optimizador = optim.Adam(
        filter(
            lambda parametro: parametro.requires_grad,
            modelo.parameters()
        ),
        lr=LEARNING_RATE
    )

    mejor_accuracy = -1.0
    mejor_perdida = float("inf")
    mejor_epoca = 0

    historial = []

    inicio_entrenamiento = time.time()

    print("\nIniciando entrenamiento...\n")

    for epoca in range(1, EPOCAS + 1):

        inicio_epoca = time.time()

        perdida_train, accuracy_train = entrenar_epoca(
            modelo,
            loader_train,
            criterio,
            optimizador
        )

        perdida_val, accuracy_val = validar_epoca(
            modelo,
            loader_val,
            criterio
        )

        duracion = time.time() - inicio_epoca

        registro = {
            "epoca": epoca,
            "train_loss": perdida_train,
            "train_accuracy": accuracy_train,
            "val_loss": perdida_val,
            "val_accuracy": accuracy_val,
            "duracion_segundos": duracion
        }

        historial.append(registro)

        print(f"Época {epoca}/{EPOCAS}")
        print(f"  Train Loss: {perdida_train:.4f}")
        print(f"  Train Accuracy: {accuracy_train * 100:.2f}%")
        print(f"  Val Loss: {perdida_val:.4f}")
        print(f"  Val Accuracy: {accuracy_val * 100:.2f}%")
        print(f"  Duración: {duracion:.2f} segundos")

        # Guardar el modelo con mejor validación

        if (
            accuracy_val > mejor_accuracy
            or (
                accuracy_val == mejor_accuracy
                and perdida_val < mejor_perdida
            )
        ):

            mejor_accuracy = accuracy_val
            mejor_perdida = perdida_val
            mejor_epoca = epoca

            torch.save(
                {
                    "arquitectura": "MobileNetV2",
                    "model_state_dict": modelo.state_dict(),
                    "class_to_idx": clases,
                    "epoca": epoca,
                    "val_accuracy": accuracy_val,
                    "val_loss": perdida_val
                },
                RUTA_MODELO
            )

            print("  Mejor modelo guardado.")

        # Guardar el historial después de cada época

        with open(
            RUTA_HISTORIAL,
            "w",
            encoding="utf-8"
        ) as archivo:

            json.dump(
                historial,
                archivo,
                indent=4,
                ensure_ascii=False
            )

        print("-" * 60)

    duracion_total = time.time() - inicio_entrenamiento

    print("\nENTRENAMIENTO FINALIZADO")
    print(f"Mejor época: {mejor_epoca}")
    print(f"Mejor Val Accuracy: {mejor_accuracy * 100:.2f}%")
    print(f"Duración total: {duracion_total:.2f} segundos")
    print(f"Modelo guardado en: {RUTA_MODELO}")
    print(f"Historial guardado en: {RUTA_HISTORIAL}")


if __name__ == "__main__":
    entrenar()