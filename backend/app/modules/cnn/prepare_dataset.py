import json
import os
import random
import shutil

from pathlib import Path
from collections import defaultdict

from PIL import Image


# Configuración general

SEMILLA = 42

RAIZ_PROYECTO = Path(__file__).resolve().parents[4]

ORIGEN = Path(os.environ["TEMP"]) / "PlantVillage-Dataset"

DESTINO = RAIZ_PROYECTO / "datasets" / "cnn"

CLASES = {
    "Pepper,_bell___healthy": "sana",
    "Pepper,_bell___Bacterial_spot": "enferma"
}

EXTENSIONES = {".jpg", ".jpeg", ".png"}

PROPORCIONES = {
    "train": 0.70,
    "validation": 0.15,
    "test": 0.15
}


def normalizar_nombre(nombre):
    return " ".join(nombre.strip().lower().split())


def cargar_metadatos():

    ruta = ORIGEN / "leaf-map.json"

    with open(ruta, encoding="utf-8") as archivo:
        datos = json.load(archivo)

    return {
        normalizar_nombre(nombre): grupos
        for nombre, grupos in datos.items()
    }


def validar_imagen(ruta):

    try:
        with Image.open(ruta) as imagen:
            imagen.verify()

        return True

    except Exception:
        return False


def obtener_grupos(carpeta, metadatos):

    grupos = defaultdict(list)

    reconocidas = 0
    sin_metadatos = 0
    invalidas = 0

    ruta = ORIGEN / "raw" / "color" / carpeta

    for imagen in sorted(ruta.iterdir()):

        if imagen.suffix.lower() not in EXTENSIONES:
            continue

        if not validar_imagen(imagen):
            invalidas += 1
            continue

        nombre_original = imagen.stem.split("___", 1)[-1]

        referencia = normalizar_nombre(nombre_original)

        coincidencias = [
            grupo
            for grupo in metadatos.get(referencia, [])
            if grupo.startswith(carpeta + ":::")
        ]

        if len(coincidencias) == 1:

            identificador = coincidencias[0]
            reconocidas += 1

        elif len(coincidencias) > 1:

            raise ValueError(
                f"Grupo ambiguo para {imagen.name}: "
                f"{coincidencias}"
            )

        else:

            identificador = f"sin_mapa::{referencia}"
            sin_metadatos += 1

        grupos[identificador].append(imagen)

    print(f"\nCategoría: {carpeta}")
    print(f"Imágenes con metadatos: {reconocidas}")
    print(f"Imágenes sin metadatos: {sin_metadatos}")
    print(f"Imágenes inválidas: {invalidas}")
    print(f"Grupos identificados: {len(grupos)}")

    return grupos


def dividir_grupos(grupos):

    elementos = list(grupos.values())

    generador = random.Random(SEMILLA)
    generador.shuffle(elementos)

    total = sum(len(grupo) for grupo in elementos)

    objetivos = {
        conjunto: total * proporcion
        for conjunto, proporcion in PROPORCIONES.items()
    }

    distribucion = {
        "train": [],
        "validation": [],
        "test": []
    }

    cantidades = {
        "train": 0,
        "validation": 0,
        "test": 0
    }

    for grupo in elementos:

        conjunto = max(
            objetivos,
            key=lambda nombre: (
                objetivos[nombre] - cantidades[nombre]
            )
        )

        distribucion[conjunto].extend(grupo)

        cantidades[conjunto] += len(grupo)

    return distribucion


def copiar_imagenes(imagenes, carpeta):

    carpeta.mkdir(parents=True, exist_ok=True)

    for imagen in imagenes:
        shutil.copy2(imagen, carpeta / imagen.name)


def preparar_dataset():

    if DESTINO.exists() and any(
        archivo.is_file()
        for archivo in DESTINO.rglob("*")
    ):
        raise FileExistsError(
            f"La carpeta {DESTINO} contiene archivos. "
            "Revísala antes de volver a preparar el dataset."
        )

    metadatos = cargar_metadatos()

    resumen = {}

    # Analizar y dividir antes de copiar archivos

    distribuciones = {}

    for carpeta_original, clase in CLASES.items():

        grupos = obtener_grupos(
            carpeta_original,
            metadatos
        )

        distribuciones[clase] = dividir_grupos(grupos)

    # Crear estructura y copiar imágenes

    for clase, distribucion in distribuciones.items():

        resumen[clase] = {}

        for conjunto, imagenes in distribucion.items():

            carpeta_destino = DESTINO / conjunto / clase

            copiar_imagenes(imagenes, carpeta_destino)

            copiar_imagenes(
                imagenes,
                DESTINO / "raw" / clase
            )

            resumen[clase][conjunto] = len(imagenes)

        (DESTINO / "external" / clase).mkdir(
            parents=True,
            exist_ok=True
        )

    # Conservar metadatos originales

    shutil.copy2(
        ORIGEN / "leaf-map.json",
        DESTINO / "leaf-map.json"
    )

    # Guardar distribución obtenida

    with open(
        DESTINO / "resumen_dataset.json",
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            resumen,
            archivo,
            indent=4,
            ensure_ascii=False
        )

    print("\n" + "=" * 50)
    print("DISTRIBUCIÓN FINAL DEL DATASET")
    print("=" * 50)

    for clase, conjuntos in resumen.items():

        print(f"\nClase: {clase}")

        for conjunto, cantidad in conjuntos.items():
            print(f"  {conjunto}: {cantidad}")

    total = sum(
        sum(conjuntos.values())
        for conjuntos in resumen.values()
    )

    print(f"\nTotal de imágenes: {total}")
    print(f"Dataset guardado en: {DESTINO}")
    print("Preparación finalizada correctamente.")


if __name__ == "__main__":
    preparar_dataset()