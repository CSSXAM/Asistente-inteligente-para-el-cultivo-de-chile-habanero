
# Asistente inteligente para el cultivo de chile habanero

## Descripción

Proyecto académico orientado al desarrollo de una aplicación web que integre técnicas de inteligencia artificial para apoyar la supervisión y el manejo del cultivo de chile habanero (*Capsicum chinense*).

La aplicación contempla tres módulos principales:

1. **Planificación de rutas mediante A\*:** permitirá calcular recorridos de inspección dentro de una parcela representada mediante una cuadrícula, considerando obstáculos, surcos y puntos de inspección.

2. **Recomendación de riego mediante lógica difusa:** utilizará variables como la humedad del suelo, la temperatura ambiental y la etapa de desarrollo del cultivo para recomendar el tiempo de riego.

3. **Clasificación de imágenes mediante CNN:** permitirá clasificar fotografías de hojas sanas y hojas que presenten síntomas de enfermedades mediante redes neuronales convolucionales.

---

## Objetivo general

Desarrollar una aplicación web que integre técnicas de inteligencia artificial, mediante la búsqueda heurística A*, la lógica difusa y las redes neuronales convolucionales, para apoyar la planificación de rutas de inspección, la recomendación del tiempo de riego y la identificación visual de posibles enfermedades en el cultivo de chile habanero (*Capsicum chinense*).

---

## Tecnologías

| Tecnología | Propósito |
|---|---|
| Python | Desarrollo de los módulos de inteligencia artificial. |
| scikit-fuzzy | Implementación del controlador de lógica difusa. |
| TensorFlow/Keras | Construcción y entrenamiento de la red neuronal convolucional. |
| FastAPI | Desarrollo de la API del sistema. |
| React | Desarrollo de la interfaz web. |
| MySQL 8 | Almacenamiento de información e historial. |

---

## Estructura prevista del proyecto

```text
chile-habanero-ia/
├── frontend/
├── backend/
│   └── app/
│       ├── modules/
│       │   ├── astar/
│       │   ├── fuzzy/
│       │   └── cnn/
│       ├── routes/
│       └── database/
├── datasets/
├── tests/
├── docs/
├── database/
└── README.md
```

La estructura se irá incorporando conforme avance la implementación.

---

## Metodología

El proyecto se gestionará mediante un enfoque ágil basado en **Scrum**, con un sprint de una semana y actividades autogestionadas.

La investigación comenzó el **6 de noviembre de 2026**, mientras que el desarrollo e implementación está programada a partir del **20 de Noviembre de 2026** hasta el **25 de Noviembre del 2026**.

Las actividades y su seguimiento se gestionarán mediante **Jira**. El código fuente y su historial de cambios se administrarán mediante **Git y GitHub**.

---

## Estado del proyecto

**En desarrollo.**

Actualmente se cuenta con investigación preliminar sobre las características del cultivo de chile habanero, sus necesidades de riego, las principales plagas y enfermedades, así como la representación de parcelas agrícolas.

### Avances

- [x] Investigación preliminar sobre el cultivo.
- [x] Revisión de fuentes bibliográficas.
- [x] Definición inicial de objetivos y alcance.
- [x] Selección de tecnologías.
- [x] Planificación del sprint en Jira.
- [ ] Implementación del algoritmo A*.
- [ ] Implementación del controlador de lógica difusa.
- [ ] Entrenamiento y evaluación de la CNN.
- [ ] Desarrollo de la aplicación web.
- [ ] Integración de los módulos.
- [ ] Pruebas y validación final.

---

## Instalación y ejecución

Las instrucciones de instalación, configuración y ejecución se incorporarán conforme se implementen los componentes del sistema.

---

## Alcance y limitaciones

El sistema se desarrollará como un **prototipo académico**.

Las recomendaciones de riego utilizarán datos simulados y los resultados de clasificación de imágenes tendrán carácter orientativo.

La aplicación no sustituirá la evaluación y el diagnóstico realizados por especialistas agrícolas.

El alcance de la clasificación de imágenes estará condicionado por la disponibilidad y calidad de los datos utilizados para el entrenamiento del modelo.

---

## Control de versiones

El desarrollo se gestionará mediante **Git y GitHub**, registrando los cambios realizados durante su desarrollo hasta su implemetación.

El repositorio contendrá el código fuente, las pruebas, la documentación técnica y las instrucciones necesarias para reproducir el funcionamiento del proyecto.

---

## Documentación

La documentación del proyecto contemplará:

- Planteamiento del problema.
- Objetivo general y objetivos específicos.
- Alcance y requerimientos.
- Metodología de desarrollo.
- Desarrollo de los módulos de inteligencia artificial.
- Pruebas y resultados.
- Conclusiones.
- Referencias bibliográficas.
- Anexos.
