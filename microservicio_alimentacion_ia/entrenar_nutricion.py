"""
Entrena el modelo de recomendación de ración diaria (regresión) usado por
POST /alimentacion/predecir_dieta.

Este servicio nunca tuvo un script de entrenamiento (a diferencia de
microservicio_ia/entrenar_ia.py o microservicio_notificaciones/entrenar_notificador.py),
por eso modelo_nutricion.pkl quedó como un archivo vacío. Sigue el mismo
patrón que esos dos: genera datos sintéticos a partir de una fórmula de
dominio real y entrena un modelo de scikit-learn sobre ellos.

Fórmula de dominio (guía de nutrición porcina estándar):
- La ración diaria como % del peso vivo baja con la edad: los lechones
  recién destetados comen ~8% de su peso, los cerdos de finalización ~2.5%.
- El estrés calórico reduce el consumo: por encima de 25°C el apetito cae
  progresivamente (mismo umbral que ya usa la ruta para la advertencia).
- Se agrega ruido gaussiano para que el modelo aprenda una aproximación,
  no memorice la fórmula exacta.
"""

import os

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor

print("Entrenando modelo de recomendación de ración (regresión)...")

np.random.seed(42)
N = 2000

edades = np.random.uniform(21, 180, N)
pesos = np.random.uniform(5, 250, N)
temperaturas = np.random.uniform(-10, 45, N)

X = []
y = []

for edad, peso, temp in zip(edades, pesos, temperaturas):
    # % del peso vivo: decrece de ~8.5% (destete) a ~2.5% (finalización)
    porcentaje_base = np.clip(8.5 - (edad / 40), 2.5, 8.5)
    racion_base = peso * (porcentaje_base / 100)

    # Estrés calórico: por encima de 25°C el consumo cae hasta un 40%
    factor_temp = 1.0
    if temp > 25:
        factor_temp = max(0.6, 1 - (temp - 25) * 0.025)

    racion = racion_base * factor_temp
    racion += np.random.normal(0, racion * 0.05)  # ruido ~5%
    racion = max(0.05, racion)

    X.append([edad, peso, temp])
    y.append(racion)

modelo = RandomForestRegressor(n_estimators=150, random_state=42)
modelo.fit(X, y)

ruta = os.path.join(os.path.dirname(__file__), "modelo_nutricion.pkl")
joblib.dump(modelo, ruta)
print(f"Modelo guardado en: {ruta}")

# Verificación rápida con un caso conocido
prueba = modelo.predict([[60, 25, 24]])[0]
print(f"Prueba — cerdo de 60 días, 25kg, 24°C -> ración recomendada: {prueba:.2f} kg")
