# D:\proyectos\Demeter\microservicio_ia_notificaciones\main.py
import os
import sys

# ---------------------------------------------------------
# INYECCIÓN AUTOMÁTICA DE RUTA PARA DEMETER_CORE
# ---------------------------------------------------------
# Calculamos la ruta absoluta hacia la carpeta 'core_compartido'
RUTA_PROYECTO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "core_compartido"))

# Si la ruta no está en sys.path, la agregamos dinámicamente al inicio
if RUTA_PROYECTO not in sys.path:
    sys.path.insert(0, RUTA_PROYECTO)
import datetime
import joblib
import pandas as pd
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from demeter_core.esquemas import DatosClimaPayload, AlertaWhatsAppPayload

app = FastAPI(
    title="Microservicio IA Notificaciones - Demeter",
    description="Evalúa reglas de Machine Learning para automatizar el despacho de alertas",
    version="1.0.0"
)

# CORS: la autenticación va por header Authorization (Bearer), no por cookies,
# así que no se necesita allow_credentials=True — combinarlo con origin "*"
# es además inválido según el spec de CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "OK", "service": "IA Notificaciones"}

# Variable global para almacenar el modelo en memoria
MODELO_DECISION = None
RUTA_MODELO = os.path.join(os.path.dirname(__file__), "modelo_decision_notificaciones.pkl")

# URL del microservicio de notificaciones real/simulado (puerto 8010, ver microservicio_notificaciones/main.py)
URL_NOTIFICACIONES_SERVICE = os.getenv("NOTIFICACIONES_URL", "http://127.0.0.1:8010").rstrip("/") + "/notificar"

class EvaluacionAlertaInput(BaseModel):
    datos_clima: DatosClimaPayload
    numero_telefono: str
    corral: str

@app.on_event("startup")
def cargar_modelo():
    global MODELO_DECISION
    if os.path.exists(RUTA_MODELO):
        MODELO_DECISION = joblib.load(RUTA_MODELO)
        print("✅ Modelo de decisión de notificaciones cargado en RAM.")
    else:
        print("⚠️ No se encontró el archivo .pkl. Ejecute entrenar_modelo.py primero.")

@app.post("/evaluar-y-notificar", tags=["Automatización ML"])
async def evaluar_y_notificar(payload: EvaluacionAlertaInput):
    """
    Recibe datos ambientales, realiza la predicción de prioridad
    y si es urgente, invoca de forma automática al microservicio_notificaciones.
    """
    if MODELO_DECISION is None:
        raise HTTPException(status_code=503, detail="Modelo ML no inicializado.")

    hora_actual = datetime.datetime.now().hour

    # Preparar el dataframe para la inferencia
    df_input = pd.DataFrame([{
        'temperatura_c': payload.datos_clima.temperatura_c,
        'humedad_pct': payload.datos_clima.humedad_pct,
        'peso_promedio_kg': payload.datos_clima.peso_promedio_kg,
        'hora_dia': hora_actual
    }])

    # Inferencia del modelo
    prediccion = int(MODELO_DECISION.predict(df_input)[0])
    probabilidades = MODELO_DECISION.predict_proba(df_input)[0].tolist()

    mapa_decisiones = {
        0: "OMITIR_NOTIFICACION",
        1: "NOTIFICAR_EMAIL",
        2: "NOTIFICAR_WHATSAPP_URGENTE"
    }

    accion_determinada = mapa_decisiones.get(prediccion, "DESCONOCIDO")
    respuesta_despacho = None

    # Automatización: Si el modelo determina WhatsApp Urgente (código 2)
    if prediccion == 2:
        payload_notificacion = {
            "numero_telefono": payload.numero_telefono,
            "corral": payload.corral,
            "racion_kg": round(payload.datos_clima.peso_promedio_kg * 0.04, 2),
            "motivo_ia": f"Alerta Crítica ML: Temp {payload.datos_clima.temperatura_c}°C y Humedad {payload.datos_clima.humedad_pct}% superan umbral de confort."
        }
        
        try:
            res = requests.post(URL_NOTIFICACIONES_SERVICE, json=payload_notificacion, timeout=5)
            respuesta_despacho = res.json() if res.status_code == 200 else f"Error HTTP {res.status_code}"
        except Exception as e:
            respuesta_despacho = f"No se pudo contactar al microservicio_notificaciones: {str(e)}"

    return {
        "codigo_decision": prediccion,
        "accion": accion_determinada,
        "certeza": max(probabilidades),
        "despacho_automatico": respuesta_despacho
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8007, reload=True)