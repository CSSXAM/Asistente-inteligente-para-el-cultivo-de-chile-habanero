from pathlib import Path
from uuid import uuid4
import logging

from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image

from app.modules.cnn.predict import predecir_imagen

from app.modules.cnn.repository import (
    guardar_clasificacion,
    obtener_historial
)


router = APIRouter(
    prefix="/api/cnn",
    tags=["CNN"]
)

logger = logging.getLogger(__name__)


# Configuración del almacenamiento

RAIZ_BACKEND = Path(__file__).resolve().parents[2]

CARPETA_UPLOADS = RAIZ_BACKEND / "uploads" / "cnn"

CARPETA_UPLOADS.mkdir(
    parents=True,
    exist_ok=True
)

MAX_ARCHIVO = 10 * 1024 * 1024

FORMATOS_PERMITIDOS = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp"
}


# Clasificar una imagen

@router.post("/clasificar")
def clasificar_imagen(imagen: UploadFile = File(...)):

    ruta_imagen = None
    registro_guardado = False

    try:

        contenido = imagen.file.read(MAX_ARCHIVO + 1)

        if not contenido:
            raise HTTPException(
                status_code=400,
                detail="La imagen está vacía."
            )

        if len(contenido) > MAX_ARCHIVO:
            raise HTTPException(
                status_code=413,
                detail="La imagen supera el límite de 10 MB."
            )

        # Verificar el formato real del archivo

        imagen.file.seek(0)

        with Image.open(imagen.file) as archivo:

            formato = archivo.format

            if formato not in FORMATOS_PERMITIDOS:
                raise HTTPException(
                    status_code=415,
                    detail="Formato de imagen no compatible."
                )

            if archivo.width * archivo.height > 20_000_000:
                raise HTTPException(
                    status_code=400,
                    detail="La resolución es demasiado grande."
                )

            archivo.verify()

        # Generar un nombre único

        extension = FORMATOS_PERMITIDOS[formato]

        nombre_archivo = f"{uuid4().hex}{extension}"

        ruta_imagen = CARPETA_UPLOADS / nombre_archivo

        # Guardar la fotografía

        ruta_imagen.write_bytes(contenido)

        # Realizar la clasificación neuronal

        resultado = predecir_imagen(ruta_imagen)

        # Obtener la ruta relativa al backend

        ruta_relativa = ruta_imagen.relative_to(
            RAIZ_BACKEND
        ).as_posix()

        nombre_original = (
            (imagen.filename or nombre_archivo)
            .replace("\\", "/")
            .split("/")[-1][:255]
        )

        # Registrar el resultado en MySQL

        id_registro = guardar_clasificacion(
            nombre_imagen=nombre_original,
            ruta_imagen=ruta_relativa,
            resultado=resultado
        )

        registro_guardado = True

        return {
            "id": id_registro,
            "nombre_imagen": nombre_original,
            "ruta_imagen": ruta_relativa,
            **resultado
        }

    except HTTPException:
        raise

    except Image.DecompressionBombError:

        raise HTTPException(
            status_code=400,
            detail="La resolución de la imagen es excesiva."
        )

    except (OSError, ValueError, SyntaxError, AssertionError) as error:

        logger.exception("Error al procesar la imagen")

        raise HTTPException(
            status_code=400,
            detail="No fue posible procesar la imagen."
        )

    except MemoryError:

        raise HTTPException(
            status_code=503,
            detail="Memoria insuficiente para procesar la imagen."
        )

    except Exception:

        logger.exception("Error en la clasificación neuronal")

        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error interno durante la clasificación."
        )

    finally:

        # Eliminar archivos si no se completó el registro

        if ruta_imagen is not None and not registro_guardado:

            try:
                ruta_imagen.unlink(missing_ok=True)
            except OSError:
                logger.exception("No se pudo eliminar la imagen")

        imagen.file.close()


# Consultar el historial

@router.get("/historial")
def consultar_historial():

    try:

        return obtener_historial()

    except Exception:

        logger.exception("Error al consultar el historial CNN")

        raise HTTPException(
            status_code=500,
            detail="No fue posible consultar el historial."
        )