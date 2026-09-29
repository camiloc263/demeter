# D:\proyectos\Demeter\microservicio_notificaciones\main.py
import logging
import os
import sys
from contextlib import asynccontextmanager

# ---------------------------------------------------------
# Inyección de ruta hacia demeter_core (librería compartida)
# ---------------------------------------------------------
RUTA_CORE_COMPARTIDO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "core_compartido"))
if RUTA_CORE_COMPARTIDO not in sys.path:
    sys.path.insert(0, RUTA_CORE_COMPARTIDO)

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import Settings
from demeter_core.ai_client import AIConfig, crear_cliente_ia
from demeter_core.esquemas import AlertaWhatsAppPayload
from services import whatsapp_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("microservicio_notificaciones")

settings = Settings()

# Cargar el modelo de decisión (ML clásico: ¿es buen momento para notificar?)
RUTA_MODELO = os.path.join(os.path.dirname(__file__), "modelo_notificador.pkl")
try:
    modelo_ia = joblib.load(RUTA_MODELO)
except Exception as e:
    logger.error("Error al cargar modelo de notificaciones: %s", e)
    modelo_ia = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Un único cliente de IA generativa (y su pool de conexiones HTTP) para todo
    # el ciclo de vida del servicio, en vez de crear uno nuevo por petición.
    if settings.AI_MESSAGES_ENABLED:
        app.state.cliente_ia = crear_cliente_ia(
            AIConfig(
                proveedor=settings.AI_PROVIDER,
                api_key=settings.AI_API_KEY,
                modelo=settings.AI_MODEL,
                base_url=settings.AI_BASE_URL,
                timeout_segundos=settings.AI_TIMEOUT_SECONDS,
                max_reintentos=settings.AI_MAX_RETRIES,
            )
        )
    else:
        app.state.cliente_ia = None

    yield

    if app.state.cliente_ia is not None:
        await app.state.cliente_ia.cerrar()


app = FastAPI(
    title="Microservicio de Notificaciones - Granja Demeter",
    description="Motor proactivo para enviar alertas a trabajadores vía WhatsApp",
    version="1.0.0",
    lifespan=lifespan,
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


class DatosEvaluacion(BaseModel):
    nombre_corral: str
    telefono_trabajador: str
    hora_del_dia: float = Field(..., ge=0, le=24)
    temperatura_actual_c: float
    horas_desde_ultima_comida: float
    raciones_pendientes_kg: float


@app.post("/evaluar_notificacion")
async def evaluar_y_notificar(datos: DatosEvaluacion):
    """La IA evalúa si es el momento perfecto para enviar un WhatsApp al operario."""

    if modelo_ia is None:
        raise HTTPException(status_code=503, detail="Modelo IA apagado.")

    entrada = [[datos.hora_del_dia, datos.temperatura_actual_c, datos.horas_desde_ultima_comida]]
    decision_ia = modelo_ia.predict(entrada)[0]

    if decision_ia != 1:
        return {
            "estado": "EN_ESPERA",
            "mensaje": "La IA determinó que AÚN NO es un buen momento (posible estrés calórico o cerdos sin apetito).",
        }

    motivo = "Temperatura fresca y horas de ayuno superadas. Máxima absorción de nutrientes garantizada."

    try:
        await whatsapp_client.enviar_alerta_whatsapp(
            numero_telefono=datos.telefono_trabajador,
            corral=datos.nombre_corral,
            racion_kg=datos.raciones_pendientes_kg,
            motivo_ia=motivo,
            cliente_ia=app.state.cliente_ia,
        )
    except Exception as exc:
        logger.error("Fallo al enviar la notificación de WhatsApp: %s", exc)
        raise HTTPException(status_code=502, detail="No se pudo enviar la notificación") from exc

    return {
        "estado": "NOTIFICACION_ENVIADA",
        "mensaje": f"Se ha enviado un WhatsApp al número {datos.telefono_trabajador}.",
    }


@app.post("/notificar")
async def notificar_directo(payload: AlertaWhatsAppPayload):
    """
    Despacha una alerta de WhatsApp ya decidida por otro servicio (p. ej.
    microservicio_ia_notificaciones, que tiene su propio modelo de decisión),
    sin volver a evaluar el modelo ML local de `/evaluar_notificacion`.
    """
    try:
        await whatsapp_client.enviar_alerta_whatsapp(
            numero_telefono=payload.numero_telefono,
            corral=payload.corral,
            racion_kg=payload.racion_kg,
            motivo_ia=payload.motivo_ia,
            cliente_ia=app.state.cliente_ia,
        )
    except Exception as exc:
        logger.error("Fallo al enviar la notificación de WhatsApp: %s", exc)
        raise HTTPException(status_code=502, detail="No se pudo enviar la notificación") from exc

    return {
        "estado": "NOTIFICACION_ENVIADA",
        "mensaje": f"Se ha enviado un WhatsApp al número {payload.numero_telefono}.",
    }


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "OK", "service": "Notificaciones"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8010, reload=True)
