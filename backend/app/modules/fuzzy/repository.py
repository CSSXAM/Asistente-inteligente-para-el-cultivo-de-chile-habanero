from ...database.connection import conectar_db

def guardar_recomendacion(resultado):
    conexion = conectar_db()
    cursor = None

    try:
        cursor = conexion.cursor()

        consulta = """
            INSERT INTO historial_riego (
                humedad,
                temperatura,
                etapa,
                minutos_riego,
                caudal_litros_hora,
                litros_estimados_por_gotero
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        valores = (
            resultado["humedad"],
            resultado["temperatura"],
            resultado["etapa"],
            resultado["minutos_riego"],
            resultado["caudal_litros_hora"],
            resultado["litros_estimados_por_gotero"]
        )

        cursor.execute(consulta, valores)

        conexion.commit()

        return cursor.lastrowid

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        conexion.close()

def obtener_historial():
    conexion = conectar_db()
    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                id,
                humedad,
                temperatura,
                etapa,
                minutos_riego,
                caudal_litros_hora,
                litros_estimados_por_gotero,
                fecha_registro
            FROM historial_riego
            ORDER BY fecha_registro DESC, id DESC
            LIMIT 100
        """

        cursor.execute(consulta)

        registros = cursor.fetchall()

        return registros

    finally:
        if cursor is not None:
            cursor.close()

        conexion.close()
        