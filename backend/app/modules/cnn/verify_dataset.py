import hashlib

from collections import defaultdict

from .prepare_dataset import (
    DESTINO,
    CLASES,
    cargar_metadatos,
    normalizar_nombre
)


def verificar_dataset():

    metadatos = cargar_metadatos()

    archivos = defaultdict(set)
    grupos = defaultdict(set)
    hashes = defaultdict(set)

    reconocidas = 0
    sin_metadatos = 0
    total = 0

    for conjunto in ["train", "validation", "test"]:

        for carpeta_original, clase in CLASES.items():

            ruta = DESTINO / conjunto / clase

            for imagen in sorted(ruta.iterdir()):

                if imagen.suffix.lower() not in {
                    ".jpg", ".jpeg", ".png"
                }:
                    continue

                total += 1

                archivos[imagen.name].add(conjunto)

                huella = hashlib.sha256(
                    imagen.read_bytes()
                ).hexdigest()

                hashes[huella].add(conjunto)

                referencia = normalizar_nombre(
                    imagen.stem.split("___", 1)[-1]
                )

                coincidencias = [
                    grupo
                    for grupo in metadatos.get(
                        referencia, []
                    )
                    if grupo.startswith(
                        carpeta_original + ":::"
                    )
                ]

                if coincidencias:

                    reconocidas += 1

                    for grupo in coincidencias:
                        grupos[grupo].add(conjunto)

                else:

                    sin_metadatos += 1

                    identificador = (
                        f"{clase}::sin_mapa::{referencia}"
                    )

                    grupos[identificador].add(conjunto)

    archivos_repetidos = [
        nombre
        for nombre, conjuntos in archivos.items()
        if len(conjuntos) > 1
    ]

    contenido_repetido = [
        huella
        for huella, conjuntos in hashes.items()
        if len(conjuntos) > 1
    ]

    grupos_separados = [
        grupo
        for grupo, conjuntos in grupos.items()
        if len(conjuntos) > 1
    ]

    print("\n=== VERIFICACIÓN DEL DATASET ===")

    print(f"Total de imágenes: {total}")
    print(f"Imágenes con metadatos: {reconocidas}")
    print(f"Imágenes sin metadatos: {sin_metadatos}")

    print(
        f"Archivos repetidos entre conjuntos: "
        f"{len(archivos_repetidos)}"
    )

    print(
        f"Contenido idéntico entre conjuntos: "
        f"{len(contenido_repetido)}"
    )

    print(
        f"Grupos separados entre conjuntos: "
        f"{len(grupos_separados)}"
    )

    if (
        total == 2475
        and not archivos_repetidos
        and not contenido_repetido
        and not grupos_separados
    ):
        print("\nRESULTADO: APROBADO")
    else:
        print("\nRESULTADO: REQUIERE REVISIÓN")


if __name__ == "__main__":
    verificar_dataset()