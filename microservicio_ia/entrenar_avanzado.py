import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

print("🌲 Entrenando Bosque Aleatorio Avanzado (100 Árboles)...")

# 1. Generamos 1000 registros sintéticos de granjas reales
np.random.seed(42) # Para que siempre generemos los mismos datos aleatorios
temperaturas = np.random.uniform(15, 45, 1000)
humedades = np.random.uniform(20, 100, 1000)
pesos = np.random.uniform(5, 250, 1000) # De lechones de 5kg a madres de 250kg

X = [] # Nuestras características (Temp, Humedad, Peso)
y = [] # Nuestras etiquetas de riesgo

for t, h, p in zip(temperaturas, humedades, pesos):
    # Fórmula científica THI (Temperature-Humidity Index)
    thi = (0.8 * t) + ((h * (t - 14.4)) / 100) + 46.4
    
    # Ajuste metabólico: Animales más pesados tienen un umbral de tolerancia menor
    ajuste_peso = p * 0.06 
    thi_ajustado = thi + ajuste_peso

    # Categorizamos el nivel de riesgo según los estándares
    if thi_ajustado < 74:
        estado = 0 # ÓPTIMO
    elif thi_ajustado < 84:
        estado = 1 # ALERTA
    else:
        estado = 2 # PELIGRO
        
    X.append([t, h, p])
    y.append(estado)

# 2. Entrenamos el Bosque Aleatorio (Ensemble Learning)
modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X, y)

# 3. Guardamos el nuevo "súper cerebro"
ruta = os.path.join(os.path.dirname(__file__), "modelo_clima_avanzado.pkl")
joblib.dump(modelo, ruta)
print(f"✅ ¡Nuevo cerebro avanzado guardado exitosamente en:\n{ruta}")