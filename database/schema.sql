CREATE DATABASE IF NOT EXISTS chile_habanero_ia;

USE chile_habanero_ia;

CREATE TABLE IF NOT EXISTS historial_riego (
    id INT AUTO_INCREMENT PRIMARY KEY,

    humedad DECIMAL(5,2) NOT NULL,
    temperatura DECIMAL(4,2) NOT NULL,
    etapa VARCHAR(20) NOT NULL,

    minutos_riego DECIMAL(4,2) NOT NULL,
    caudal_litros_hora DECIMAL(5,2) NOT NULL,
    litros_estimados_por_gotero DECIMAL(6,3) NOT NULL,

    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_humedad
        CHECK (humedad BETWEEN 0 AND 100),

    CONSTRAINT chk_temperatura
        CHECK (temperatura BETWEEN 0 AND 50),

    CONSTRAINT chk_etapa
        CHECK (etapa IN (
            'vivero',
            'trasplante',
            'vegetativo',
            'floracion',
            'fructificacion',
            'cosecha'
        )),

    CONSTRAINT chk_minutos_riego
        CHECK (minutos_riego BETWEEN 0 AND 60),

    CONSTRAINT chk_caudal
        CHECK (caudal_litros_hora > 0),

    CONSTRAINT chk_litros
        CHECK (litros_estimados_por_gotero >= 0)
);

USE chile_habanero_ia;

CREATE TABLE IF NOT EXISTS historial_cnn (
    id INT AUTO_INCREMENT PRIMARY KEY,

    nombre_imagen VARCHAR(255) NOT NULL,

    ruta_imagen VARCHAR(500) NOT NULL,

    clase ENUM('sana', 'enferma') NOT NULL,

    diagnostico VARCHAR(100) NOT NULL,

    confianza DECIMAL(5,2) NOT NULL,

    probabilidad_enferma DECIMAL(5,2) NOT NULL,

    probabilidad_sana DECIMAL(5,2) NOT NULL,

    recomendacion TEXT NOT NULL,

    fecha_registro DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);