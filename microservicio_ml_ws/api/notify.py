from fastapi import APIRouter, HTTPException
import httpx
import os

from demeter_core.esquemas import AlertaWhatsAppPayload

router = APIRouter()

# microservicio_notificaciones corre en el puerto 8010 y expone /notificar
# (ver microservicio_notificaciones/main.py). El valor anterior aquí
# ("http://localhost:8000/notify") apuntaba al puerto de otro servicio
# (microservicio_alimentacion) y a una ruta que nunca existió.
NOTIFICATIONS_SERVICE_URL = os.getenv(
    "NOTIFICATIONS_URL", "http://127.0.0.1:8010"
).rstrip("/") + "/notificar"

@router.post("/send-notification")
async def send_notification(payload: AlertaWhatsAppPayload):
    """
    Reenvía una alerta ya armada hacia microservicio_notificaciones:8010/notificar.
    Es un simple proxy — la validación y el envío real los hace ese servicio.
    """
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.post(NOTIFICATIONS_SERVICE_URL, json=payload.model_dump())
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail="microservicio_notificaciones no está disponible") from exc

        if response.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Failed to notify (HTTP {response.status_code})")
        return {"status": "forwarded", "detail": response.json()}