# D:\proyectos\Demeter\microservicio_ia_notificaciones\entrenar_modelo.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

def generar_datos_y_entrenar():
    np.random.seed(42)
    n_muestras = 1000

    # Generación de características sintéticas para las alertas
    temperatura = np.random.uniform(18.0, 38.0, n_muestras)
    humedad = np.random.uniform(40.0, 95.0, n_muestras)
    peso_promedio = np.random.uniform(15.0, 110.0, n_muestras)
    hora_dia = np.random.randint(0, 24, n_muestras)

    # Regla lógica de etiquetado (0: No notificar, 1: Email, 2: WhatsApp Urgente)
    etiquetas = []
    for t, h, p in zip(temperatura, humedad, peso_promedio):
        # Índice simplificado de estrés térmico
        thi = 0.8 * t + (h / 100.0) * (t - 14.3) + 46.4
        
        if thi > 78.0 or t > 32.0:
            etiquetas.append(2)  # WHATSAPP_URGENTE
        elif thi > 72.0 or t > 28.0:
            etiquetas.append(1)  # ENVIAR_CORREO
        else:
            etiquetas.append(0)  # NO_ENVIAR

    X = pd.DataFrame({
        'temperatura_c': temperatura,
        'humedad_pct': humedad,
        'peso_promedio_kg': peso_promedio,
        'hora_dia': hora_dia
    })
    y = np.array(etiquetas)

    # Entrenamiento del modelo Random Forest
    modelo = RandomForestClassifier(n_estimators=50, random_state=42)
    modelo.fit(X, y)

    # Guardar modelo entrenado
    joblib.dump(modelo, "modelo_decision_notificaciones.pkl")
    print("✅ Modelo 'modelo_decision_notificaciones.pkl' generado exitosamente.")

if __name__ == "__main__":
    generar_datos_y_entrenar()