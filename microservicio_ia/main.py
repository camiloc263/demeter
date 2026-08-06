from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import os

app = FastAPI(
    title="IA Avanzada Demeter - Random Forest",
    description="Motor de Machine Learning con análisis predictivo multidimensional",
    version="2.0.0"
)

# Cargamos el nuevo modelo avanzado
RUTA_MODELO = os.path.join(os.path.dirname(__file__), "modelo_clima_avanzado.pkl")
try:
    modelo_ia = joblib.load(RUTA_MODELO)
    print("🌲 Bosque Aleatorio de IA cargado correctamente.")
except Exception as e:
    print(f"❌ Error al cargar el modelo avanzado: {e}")

# Añadimos el peso al modelo de validación
class DatosClimaAvanzado(BaseModel):
    temperatura_c: float = Field(..., ge=-10, le=55, description="Temperatura lógica (-10°C a 55°C)")
    humedad_pct: float = Field(..., ge=0, le=100, description="Humedad relativa (0-100%)")
    peso_promedio_kg: float = Field(..., gt=0, le=350, description="Peso promedio de los cerdos en el corral (kg)")

@app.post("/predecir")
def predecir_riesgo(datos: DatosClimaAvanzado):
    """Evalúa la temperatura, humedad y masa corporal para determinar el riesgo exacto."""
    try:
        entrada = [[datos.temperatura_c, datos.humedad_pct, datos.peso_promedio_kg]]
        
        # Obtenemos la predicción cruda
        prediccion = modelo_ia.predict(entrada)
        estado_codigo = int(prediccion[0])
        
        # Novedad: Obtenemos el porcentaje de certeza de los 100 árboles
        probabilidades = modelo_ia.predict_proba(entrada)[0]
        certeza = round(probabilidades[estado_codigo] * 100, 2)
        
        traductor = {
            0: "ÓPTIMO - Los cerdos están confortables.",
            1: "ALERTA - Posible inicio de estrés calórico.",
            2: "PELIGRO - Riesgo inminente de infarto."
        }
        
        return {
            "estado_codigo": estado_codigo,
            "mensaje": traductor.get(estado_codigo),
            "certeza_porcentaje": certeza,
            "analisis_modelo": "RandomForestClassifier (100 estimators)"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la predicción: {str(e)}")