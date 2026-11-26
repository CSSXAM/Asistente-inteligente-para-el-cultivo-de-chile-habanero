from pathlib import Path
from functools import lru_cache

import torch

from PIL import Image, ImageOps

from .model import crear_modelo
from .preprocessing import obtener_transformaciones_evaluacion


# Configuración

CARPETA_MODELOS = (
    Path(__file__).resolve().parent / "models"
)

RUTA_MODELO = CARPETA_MODELOS / "clasificador.pth"

DISPOSITIVO = torch.device("cpu")

CLASES = {
    0: "enferma",
    1: "sana"
}

TRANSFORMACION = obtener_transformaciones_evaluacion()

MAX_PIXELES = 20_000_000


# Cargar el modelo una sola vez

@lru_cache(maxsize=1)
def cargar_modelo():

    if not RUTA_MODELO.is_file():
        raise FileNotFoundError(
            "No se encontró el modelo entrenado."
        )

    checkpoint = torch.load(
        RUTA_MODELO,
        map_location=DISPOSITIVO,
        weights_only=True
    )

    if checkpoint["class_to_idx"] != {
        "enferma": 0,
        "sana": 1
    }:
        raise ValueError(
            "Las clases del modelo no coinciden."
        )

    modelo = crear_modelo(
        preentrenado=False
    ).to(DISPOSITIVO)

    modelo.load_state_dict(
        checkpoint["model_state_dict"]
    )

    modelo.eval()

    return modelo


# Procesamiento y clasificación

def predecir_imagen(ruta_imagen):

    modelo = cargar_modelo()

    with Image.open(ruta_imagen) as imagen:

        if imagen.format not in {
            "JPEG", "PNG", "WEBP"
        }:
            raise ValueError(
                "Formato de imagen no compatible."
            )

        if imagen.width * imagen.height > MAX_PIXELES:
            raise ValueError(
                "La resolución de la imagen es demasiado grande."
            )

        imagen.thumbnail((800, 800))

        imagen_rgb = ImageOps.exif_transpose(
            imagen
        ).convert("RGB")

        tensor = TRANSFORMACION(
            imagen_rgb
        ).unsqueeze(0).to(DISPOSITIVO)

    with torch.inference_mode():

        salida = modelo(tensor)

        probabilidades = torch.softmax(
            salida,
            dim=1
        )

        confianza, indice = probabilidades.max(dim=1)

    clase = CLASES[indice.item()]

    if clase == "enferma":

        diagnostico = "Posible mancha bacteriana"

        recomendacion = (
            "Inspeccionar la hoja y solicitar una "
            "verificación fitosanitaria especializada."
        )

    else:

        diagnostico = "Clasificada como sana"

        recomendacion = (
            "Continuar con la inspección periódica "
            "del cultivo."
        )

    return {
        "clase": clase,

        "diagnostico": diagnostico,

        "confianza": round(
            confianza.item() * 100, 2
        ),

        "probabilidad_enferma": round(
            probabilidades[0][0].item() * 100, 2
        ),

        "probabilidad_sana": round(
            probabilidades[0][1].item() * 100, 2
        ),

        "recomendacion": recomendacion,

        "advertencia": (
            "Resultado experimental. El modelo fue "
            "entrenado con imágenes de pimiento y "
            "no está validado para el diagnóstico "
            "fitosanitario del chile habanero."
        )
    }


# Prueba independiente del módulo

if __name__ == "__main__":

    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Clasificación neuronal de hojas"
    )

    parser.add_argument(
        "imagen",
        help="Ruta de la imagen que se desea clasificar"
    )

    argumentos = parser.parse_args()

    resultado = predecir_imagen(
        argumentos.imagen
    )

    print(
        json.dumps(
            resultado,
            indent=4,
            ensure_ascii=False
        )
    )