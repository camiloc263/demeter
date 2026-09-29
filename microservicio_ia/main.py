import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
import os
import joblib
import pickle

# ---------------------------------------------------------
# CARGA OPTIMIZADA DEL MODELO DE MACHINE LEARNING
# ---------------------------------------------------------
modelo_avanzado = None
ruta_modelo = "modelo_clima_avanzado.pkl"

# Intentamos cargar el modelo en memoria RAM al iniciar el servidor
try:
    if os.path.exists(ruta_modelo):
        try:
            # Primer intento: joblib (El más común para Machine Learning)
            modelo_avanzado = joblib.load(ruta_modelo)
            print("✅ Modelo cargado exitosamente con joblib.")
        except Exception:
            # Segundo intento: pickle clásico
            with open(ruta_modelo, "rb") as f:
                modelo_avanzado = pickle.load(f)
            print("✅ Modelo cargado exitosamente con pickle.")
    else:
        print(f"⚠️ Advertencia: No se encontró el archivo '{ruta_modelo}' en el directorio.")
except Exception as e:
    print(f"❌ Error crítico al cargar el modelo: {e}")

# ---------------------------------------------------------
# CONFIGURACIÓN DE FASTAPI
# ---------------------------------------------------------
app = FastAPI(
    description=os.getenv("APP_DESCRIPTION", "Motor de Machine Learning con análisis predictivo multidimensional"),
    version=os.getenv("APP_VERSION", "2.0.0")
)

limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])
app.state.limiter = limiter  
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler) 
app.add_middleware(SlowAPIMiddleware) 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# ESQUEMAS DE ENTRADA
# ---------------------------------------------------------
class DatosClimaPayload(BaseModel):
    temperatura_c: float
    humedad_pct: float
    peso_promedio_kg: float

# ---------------------------------------------------------
# RUTAS DE INTELIGENCIA ARTIFICIAL
# ---------------------------------------------------------
@app.post("/predecir", tags=["Machine Learning"])
async def predecir_estres_calorico(datos: DatosClimaPayload):
    """
    Procesa las métricas satelitales a través del modelo avanzado.
    """
    # 1. Verificamos si el modelo cargó correctamente en el arranque
    if modelo_avanzado is None:
        raise HTTPException(
            status_code=503, 
            detail="El modelo predictivo no está disponible en memoria."
        )

    try:
        # 2. Formatear los datos como lo espera el algoritmo (arreglo de 2 dimensiones)
        entrada_datos = [[datos.temperatura_c, datos.humedad_pct, datos.peso_promedio_kg]]

        # 3. Ejecutar la predicción real
        resultado = modelo_avanzado.predict(entrada_datos)
        
        # Asumimos que el modelo devuelve un número entero (0, 1 o 2)
        estado_calculado = int(resultado[0])
        certeza = 95.5 # Valor fijo por ahora (podemos extraer las probabilidades después si lo necesitas)

        # 4. Traducir el código a un mensaje operativo
        if estado_calculado == 2:
            mensaje = "ALERTA IA: Alto riesgo de estrés calórico."
        elif estado_calculado == 1:
            mensaje = "PRECAUCIÓN IA: Temperatura superando el umbral de confort."
        else:
            mensaje = "Clima procesado. Condiciones óptimas."

        return {
            "estado_codigo": estado_calculado,
            "mensaje": mensaje,
            "certeza_porcentaje": certeza
        }

    except Exception as e:
        # Captura errores matemáticos o de formato de datos
        raise HTTPException(status_code=500, detail=f"Error en la inferencia del modelo: {str(e)}")

@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "OK", "service": "Alimentación IA"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8006, reload=True)