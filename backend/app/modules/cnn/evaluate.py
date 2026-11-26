import json
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder

from PIL import Image

import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay
)

from .model import crear_modelo
from .preprocessing import obtener_transformaciones_evaluacion


# Configuración

RAIZ_PROYECTO = Path(__file__).resolve().parents[4]

DATASET = RAIZ_PROYECTO / "datasets" / "cnn"

CARPETA_MODELOS = Path(__file__).resolve().parent / "models"

RUTA_MODELO = CARPETA_MODELOS / "clasificador.pth"

RUTA_HISTORIAL = (
    CARPETA_MODELOS / "historial_entrenamiento.json"
)

CARPETA_RESULTADOS = CARPETA_MODELOS / "resultados"

DISPOSITIVO = torch.device("cpu")

CLASES = ["enferma", "sana"]

BATCH_SIZE = 8


# Cargar el modelo entrenado

def cargar_modelo():

    checkpoint = torch.load(
        RUTA_MODELO,
        map_location=DISPOSITIVO,
        weights_only=True
    )

    if checkpoint["class_to_idx"] != {
        "enferma": 0,
        "sana": 1
    }:
        raise ValueError("Las clases del modelo no coinciden.")

    modelo = crear_modelo(
        preentrenado=False
    ).to(DISPOSITIVO)

    modelo.load_state_dict(
        checkpoint["model_state_dict"]
    )

    modelo.eval()

    print(f"Modelo cargado: {checkpoint['arquitectura']}")
    print(f"Época seleccionada: {checkpoint['epoca']}")
    print(f"Dispositivo: {DISPOSITIVO}")

    return modelo


# Evaluación del conjunto de pruebas

def evaluar_test(modelo):

    datos_test = ImageFolder(
        root=DATASET / "test",
        transform=obtener_transformaciones_evaluacion()
    )

    if datos_test.class_to_idx != {
        "enferma": 0,
        "sana": 1
    }:
        raise ValueError("Las clases de prueba no coinciden.")

    loader = DataLoader(
        datos_test,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
        pin_memory=DISPOSITIVO.type == "cuda"
    )

    criterio = nn.CrossEntropyLoss()

    etiquetas_reales = []
    etiquetas_predichas = []

    perdida_total = 0.0

    with torch.inference_mode():

        for imagenes, etiquetas in loader:

            imagenes = imagenes.to(DISPOSITIVO)
            etiquetas = etiquetas.to(DISPOSITIVO)

            salidas = modelo(imagenes)

            perdida = criterio(salidas, etiquetas)

            perdida_total += (
                perdida.item() * etiquetas.size(0)
            )

            predicciones = salidas.argmax(dim=1)

            etiquetas_reales.extend(
                etiquetas.cpu().tolist()
            )

            etiquetas_predichas.extend(
                predicciones.cpu().tolist()
            )

    matriz = confusion_matrix(
        etiquetas_reales,
        etiquetas_predichas,
        labels=[0, 1]
    )

    resultados = {
        "total_imagenes": len(datos_test),

        "loss": perdida_total / len(datos_test),

        "accuracy": accuracy_score(
            etiquetas_reales,
            etiquetas_predichas
        ),

        "precision_macro": precision_score(
            etiquetas_reales,
            etiquetas_predichas,
            average="macro",
            zero_division=0
        ),

        "recall_macro": recall_score(
            etiquetas_reales,
            etiquetas_predichas,
            average="macro",
            zero_division=0
        ),

        "f1_macro": f1_score(
            etiquetas_reales,
            etiquetas_predichas,
            average="macro",
            zero_division=0
        ),

        "matriz_confusion": matriz.tolist(),

        "reporte_clasificacion": classification_report(
            etiquetas_reales,
            etiquetas_predichas,
            labels=[0, 1],
            target_names=CLASES,
            output_dict=True,
            zero_division=0
        )
    }

    print("\n" + "=" * 60)
    print("RESULTADOS DEL CONJUNTO DE PRUEBAS")
    print("=" * 60)

    print(f"Total de imágenes: {len(datos_test)}")
    print(f"Loss: {resultados['loss']:.4f}")

    print(
        f"Accuracy: {resultados['accuracy'] * 100:.2f}%"
    )

    print(
        f"Precision macro: "
        f"{resultados['precision_macro'] * 100:.2f}%"
    )

    print(
        f"Recall macro: "
        f"{resultados['recall_macro'] * 100:.2f}%"
    )

    print(
        f"F1-score macro: "
        f"{resultados['f1_macro'] * 100:.2f}%"
    )

    print("\nMatriz de confusión:")
    print(matriz)

    print("\nReporte de clasificación:")

    print(
        classification_report(
            etiquetas_reales,
            etiquetas_predichas,
            labels=[0, 1],
            target_names=CLASES,
            digits=4,
            zero_division=0
        )
    )

    with open(
        CARPETA_RESULTADOS / "metricas_test.json",
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            resultados,
            archivo,
            indent=4,
            ensure_ascii=False
        )

    generar_matriz_confusion(matriz)

    return resultados


# Generar matriz de confusión

def generar_matriz_confusion(matriz):

    fig, ax = plt.subplots(figsize=(7, 6))

    visualizacion = ConfusionMatrixDisplay(
        confusion_matrix=matriz,
        display_labels=["Enferma", "Sana"]
    )

    visualizacion.plot(
        cmap="Blues",
        values_format="d",
        ax=ax
    )

    ax.set_title("Matriz de confusión - MobileNetV2")
    ax.set_xlabel("Clase predicha")
    ax.set_ylabel("Clase real")

    fig.tight_layout()

    fig.savefig(
        CARPETA_RESULTADOS / "matriz_confusion.png",
        dpi=300
    )

    plt.close(fig)


# Generar curvas de aprendizaje

def generar_curvas():

    with open(
        RUTA_HISTORIAL,
        "r",
        encoding="utf-8"
    ) as archivo:

        historial = json.load(archivo)

    epocas = [
        registro["epoca"]
        for registro in historial
    ]

    train_accuracy = [
        registro["train_accuracy"] * 100
        for registro in historial
    ]

    val_accuracy = [
        registro["val_accuracy"] * 100
        for registro in historial
    ]

    train_loss = [
        registro["train_loss"]
        for registro in historial
    ]

    val_loss = [
        registro["val_loss"]
        for registro in historial
    ]

    # Gráfica de exactitud

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.plot(
        epocas,
        train_accuracy,
        marker="o",
        label="Entrenamiento"
    )

    ax.plot(
        epocas,
        val_accuracy,
        marker="o",
        label="Validación"
    )

    ax.set_title("Exactitud durante el entrenamiento")
    ax.set_xlabel("Época")
    ax.set_ylabel("Accuracy (%)")
    ax.set_xticks(epocas)
    ax.set_ylim(0, 100)
    ax.legend()
    ax.grid(alpha=0.3)

    fig.tight_layout()

    fig.savefig(
        CARPETA_RESULTADOS / "curva_accuracy.png",
        dpi=300
    )

    plt.close(fig)

    # Gráfica de pérdida

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.plot(
        epocas,
        train_loss,
        marker="o",
        label="Entrenamiento"
    )

    ax.plot(
        epocas,
        val_loss,
        marker="o",
        label="Validación"
    )

    ax.set_title("Pérdida durante el entrenamiento")
    ax.set_xlabel("Época")
    ax.set_ylabel("Loss")
    ax.set_xticks(epocas)
    ax.legend()
    ax.grid(alpha=0.3)

    fig.tight_layout()

    fig.savefig(
        CARPETA_RESULTADOS / "curva_loss.png",
        dpi=300
    )

    plt.close(fig)


# Evaluación exploratoria de imágenes externas

def evaluar_externas(modelo):

    carpeta_externa = DATASET / "external"

    transformacion = obtener_transformaciones_evaluacion()

    extensiones = {
        ".jpg", ".jpeg", ".png", ".webp"
    }

    resultados = []

    print("\n" + "=" * 60)
    print("EVALUACIÓN EXTERNA EXPLORATORIA")
    print("=" * 60)

    for clase_referencia in CLASES:

        carpeta = carpeta_externa / clase_referencia

        if not carpeta.exists():
            continue

        for ruta in sorted(carpeta.iterdir()):

            if not ruta.is_file():
                continue

            if ruta.suffix.lower() not in extensiones:
                continue

            try:

                with Image.open(ruta) as imagen:

                    imagen.thumbnail((800, 800))

                    imagen_rgb = imagen.convert("RGB")

                    tensor = transformacion(
                        imagen_rgb
                ).unsqueeze(0).to(DISPOSITIVO)

                with torch.inference_mode():

                    salida = modelo(tensor)

                    probabilidades = torch.softmax(
                        salida,
                        dim=1
                    )

                    confianza, indice = (
                        probabilidades.max(dim=1)
                    )

                prediccion = CLASES[indice.item()]

                registro = {
                    "imagen": ruta.name,
                    "clase_referencia": clase_referencia,
                    "prediccion": prediccion,
                    "confianza": confianza.item(),
                    "coincidencia": (
                        prediccion == clase_referencia
                    )
                }

                resultados.append(registro)

                print(
                    f"{ruta.name} | "
                    f"Referencia: {clase_referencia} | "
                    f"Predicción: {prediccion} | "
                    f"Confianza: "
                    f"{confianza.item() * 100:.2f}%"
                )

            except (OSError, ValueError, MemoryError, AssertionError) as error:

                print(f"Error en {ruta.name}: {error}")

    total = len(resultados)

    coincidencias = sum(
        registro["coincidencia"]
        for registro in resultados
    )

    resumen = {
        "tipo": "Evaluación externa exploratoria",

        "total_imagenes": total,

        "coincidencias": coincidencias,

        "porcentaje_coincidencia": (
            coincidencias / total * 100
            if total > 0 else None
        ),

        "limitacion": (
            "Etiquetas de referencia sin confirmación "
            "fitosanitaria. No constituye una validación "
            "clínica ni de campo."
        ),

        "predicciones": resultados
    }

    print(f"\nImágenes externas evaluadas: {total}")
    print(f"Coincidencias: {coincidencias}/{total}")

    if total > 0:

        print(
            f"Porcentaje de coincidencia: "
            f"{coincidencias / total * 100:.2f}%"
        )

    else:
        print("No se encontraron imágenes externas.")

    with open(
        CARPETA_RESULTADOS / "evaluacion_externa.json",
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            resumen,
            archivo,
            indent=4,
            ensure_ascii=False
        )

    return resumen


# Función principal

def evaluar():

    CARPETA_RESULTADOS.mkdir(
        parents=True,
        exist_ok=True
    )

    modelo = cargar_modelo()

    # Evaluación interna previamente completada
    # evaluar_test(modelo)

    # Gráficas previamente generadas
    # generar_curvas()

    evaluar_externas(modelo)

    print("\n" + "=" * 60)
    print("EVALUACIÓN EXTERNA FINALIZADA")
    print("=" * 60)

    print(
        f"Resultados guardados en: "
        f"{CARPETA_RESULTADOS}"
    )


if __name__ == "__main__":
    evaluar()