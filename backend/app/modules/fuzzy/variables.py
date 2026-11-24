import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


# ==========================================
# VARIABLES DE ENTRADA (ANTECEDENTES)
# ==========================================

# Agua aprovechable restante (%)
humedad = ctrl.Antecedent(
    np.arange(0, 101, 1),
    'humedad'
)

# Temperatura ambiental (°C)
temperatura = ctrl.Antecedent(
    np.arange(0, 50.1, 0.1),
    'temperatura'
)

# Etapa fenológica del cultivo
etapa = ctrl.Antecedent(
    np.arange(1, 7, 1),
    'etapa'
)


# ==========================================
# VARIABLE DE SALIDA (CONSECUENTE)
# ==========================================

riego = ctrl.Consequent(
    np.arange(0, 60.1, 0.1),
    'riego'
)

riego.defuzzify_method = 'centroid'


# ==========================================
# FUNCIONES DE PERTENENCIA: HUMEDAD
# ==========================================

humedad['muy_seca'] = fuzz.trapmf(
    humedad.universe, [0, 0, 20, 35]
)

humedad['seca'] = fuzz.trimf(
    humedad.universe, [20, 40, 60]
)

humedad['moderada'] = fuzz.trimf(
    humedad.universe, [45, 65, 80]
)

humedad['optima'] = fuzz.trapmf(
    humedad.universe, [70, 80, 90, 95]
)

humedad['muy_humeda'] = fuzz.trapmf(
    humedad.universe, [90, 95, 100, 100]
)


# ==========================================
# FUNCIONES DE PERTENENCIA: TEMPERATURA
# ==========================================

temperatura['fria'] = fuzz.trapmf(
    temperatura.universe, [0, 0, 15, 22]
)

temperatura['templada'] = fuzz.trimf(
    temperatura.universe, [15, 22, 26]
)

temperatura['optima'] = fuzz.trapmf(
    temperatura.universe, [23, 26, 30, 34]
)

temperatura['caliente'] = fuzz.trimf(
    temperatura.universe, [30, 34, 40]
)

temperatura['muy_caliente'] = fuzz.trapmf(
    temperatura.universe, [34, 40, 50, 50]
)


# ==========================================
# FUNCIONES DE PERTENENCIA: ETAPAS
# ==========================================

ETAPAS = {
    1: 'vivero',
    2: 'trasplante',
    3: 'vegetativo',
    4: 'floracion',
    5: 'fructificacion',
    6: 'cosecha'
}

for valor, nombre in ETAPAS.items():
    etapa[nombre] = (
        etapa.universe == valor
    ).astype(float)


# ==========================================
# FUNCIONES DE PERTENENCIA: RIEGO
# ==========================================

riego['nulo'] = fuzz.trapmf(
    riego.universe, [0, 0, 1, 3]
)

riego['muy_corto'] = fuzz.trimf(
    riego.universe, [0, 5, 10]
)

riego['corto'] = fuzz.trimf(
    riego.universe, [5, 12, 20]
)

riego['medio'] = fuzz.trimf(
    riego.universe, [15, 25, 35]
)

riego['largo'] = fuzz.trimf(
    riego.universe, [30, 40, 50]
)

riego['muy_largo'] = fuzz.trapmf(
    riego.universe, [45, 55, 60, 60]
)