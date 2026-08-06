from sklearn.tree import DecisionTreeClassifier
import joblib
import os

print("Entrenando modelo...")

# 1. Datos de entrenamiento [Temperatura, Humedad, Estado]
datos = [
    [22.0, 50.0, 0], [24.0, 55.0, 0], [26.0, 60.0, 0], [28.0, 50.0, 0], 
    [29.0, 75.0, 1], [30.0, 65.0, 1], [31.0, 50.0, 1], [32.0, 45.0, 1], 
    [33.0, 80.0, 2], [34.0, 70.0, 2], [35.0, 60.0, 2], [36.0, 85.0, 2]  
]

X = [[fila[0], fila[1]] for fila in datos]
y = [fila[2] for fila in datos]

# 2. Entrenar
modelo = DecisionTreeClassifier(random_state=42)
modelo.fit(X, y)

# 3. Guardar en la misma carpeta donde se ejecuta este script
ruta_guardado = os.path.join(os.path.dirname(__file__), "modelo_clima.pkl")
joblib.dump(modelo, ruta_guardado)

print(f"✅ ¡Cerebro creado y guardado exitosamente en:\n{ruta_guardado}")