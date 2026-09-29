import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

print("📲 Entrenando IA de Notificaciones Proactivas...")

# Características: [hora_del_dia (0-24), temperatura_actual_c, horas_desde_ultima_comida]
# Etiqueta: 1 = Enviar WhatsApp AHORA (Es el momento óptimo), 0 = Esperar (Hace calor o acaban de comer)
X = []
y = []

np.random.seed(42)
for _ in range(2000):
    hora = np.random.uniform(5, 20) # De 5 AM a 8 PM
    temp = np.random.uniform(15, 38)
    horas_ayuno = np.random.uniform(0, 16)
    
    enviar_mensaje = 0
    
    # Reglas biológicas para entrenar a la IA:
    # 1. Si llevan más de 8 horas sin comer y la temperatura es menor a 27°C -> ¡A comer!
    if horas_ayuno > 8 and temp < 27:
        enviar_mensaje = 1
    # 2. Si llevan más de 12 horas sin comer, hay que darles algo urgente, aunque haga un poco de calor (hasta 30°C)
    elif horas_ayuno > 12 and temp < 30:
        enviar_mensaje = 1
    # 3. Si hace más de 30°C, NO avisar (se desperdiciará la comida por estrés calórico)
    elif temp >= 30:
        enviar_mensaje = 0

    X.append([hora, temp, horas_ayuno])
    y.append(enviar_mensaje)

modelo_notificaciones = RandomForestClassifier(n_estimators=50, random_state=42)
modelo_notificaciones.fit(X, y)

ruta = os.path.join(os.path.dirname(__file__), "modelo_notificador.pkl")
joblib.dump(modelo_notificaciones, ruta)
print(f"✅ ¡Cerebro de notificaciones guardado en:\n{ruta}")