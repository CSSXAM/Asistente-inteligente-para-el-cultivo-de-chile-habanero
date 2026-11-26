from app.database.connection import conectar_db


# Registrar una clasificación neuronal

def guardar_clasificacion(nombre_imagen, ruta_imagen, resultado):

    conexion = conectar_db()
    cursor = None

    try:

        cursor = conexion.cursor()

        consulta = """
            INSERT INTO historial_cnn (
                nombre_imagen,
                ruta_imagen,
                clase,
                diagnostico,
                confianza,
                probabilidad_enferma,
                probabilidad_sana,
                recomendacion
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        valores = (
            nombre_imagen,
            ruta_imagen,
            resultado["clase"],
            resultado["diagnostico"],
            resultado["confianza"],
            resultado["probabilidad_enferma"],
            resultado["probabilidad_sana"],
            resultado["recomendacion"]
        )

        cursor.execute(consulta, valores)

        id_registro = cursor.lastrowid

        conexion.commit()

        return id_registro

    except Exception:

        conexion.rollback()
        raise

    finally:

        if cursor is not None:
            cursor.close()

        conexion.close()


# Consultar el historial de clasificaciones

def obtener_historial():

    conexion = conectar_db()
    cursor = None

    try:

        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                id,
                nombre_imagen,
                ruta_imagen,
                clase,
                diagnostico,
                confianza,
                probabilidad_enferma,
                probabilidad_sana,
                recomendacion,
                fecha_registro
            FROM historial_cnn
            ORDER BY fecha_registro DESC, id DESC
        """

        cursor.execute(consulta)

        registros = cursor.fetchall()

        for registro in registros:

            registro["confianza"] = float(
                registro["confianza"]
            )

            registro["probabilidad_enferma"] = float(
                registro["probabilidad_enferma"]
            )

            registro["probabilidad_sana"] = float(
                registro["probabilidad_sana"]
            )

        return registros

    finally:

        if cursor is not None:
            cursor.close()

        conexion.close()