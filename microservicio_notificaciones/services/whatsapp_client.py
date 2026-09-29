"""Cliente de envío de alertas por WhatsApp para el microservicio de notificaciones.

El texto del mensaje puede componerse de dos formas:
- Con un `BaseAIClient` (Claude/OpenAI/vLLM, ver `demeter_core.ai_client`): la IA
  redacta una alerta natural en español a partir de los datos estructurados.
- Sin cliente de IA (o si la llamada falla): se usa una plantilla fija, para que
  el envío nunca dependa de la disponibilidad del proveedor de IA.
"""

from __future__ import annotations

import datetime
import logging
from typing import Optional

from demeter_core.ai_client import AIClientError, BaseAIClient

logger = logging.getLogger("microservicio_notificaciones.whatsapp_client")

_SYSTEM_PROMPT = (
    "Eres el asistente de la granja porcícola Demeter. Redacta una alerta corta "
    "de WhatsApp en español para un trabajador de campo, con emojis, tono claro "
    "y profesional. Máximo 4 líneas, sin inventar datos fuera de los provistos."
)


def _plantilla_fija(corral: str, racion_kg: float, motivo_ia: str, hora_actual: str) -> str:
    """Mensaje de respaldo, sin dependencias externas: siempre disponible."""
    return (
        f"🐖 *Demeter AI - Orden de Alimentación*\n\n"
        f"¡Hola! Es el momento óptimo para alimentar a los cerdos.\n\n"
        f"📍 *Ubicación:* {corral}\n"
        f"⚖️ *Cantidad a preparar:* {racion_kg} kg\n"
        f"⏰ *Hora de evaluación:* {hora_actual}\n\n"
        f"🧠 *Análisis de la IA:* {motivo_ia}\n\n"
        f"Por favor, revisa el sistema para ver la orden de trabajo detallada."
    )


async def generar_mensaje_alerta(
    corral: str,
    racion_kg: float,
    motivo_ia: str,
    cliente_ia: Optional[BaseAIClient] = None,
) -> str:
    """Compone el texto de la alerta, delegando la redacción a la IA si hay cliente disponible."""
    hora_actual = datetime.datetime.now().strftime("%I:%M %p")

    if cliente_ia is None:
        return _plantilla_fija(corral, racion_kg, motivo_ia, hora_actual)

    prompt = (
        f"Corral: {corral}\n"
        f"Ración a preparar: {racion_kg} kg\n"
        f"Hora de evaluación: {hora_actual}\n"
        f"Motivo detectado por el modelo de decisión: {motivo_ia}"
    )
    try:
        return await cliente_ia.generar_texto(prompt, system=_SYSTEM_PROMPT)
    except AIClientError as exc:
        logger.warning("Fallo al generar mensaje con IA, usando plantilla fija: %s", exc)
        return _plantilla_fija(corral, racion_kg, motivo_ia, hora_actual)


async def enviar_alerta_whatsapp(
    numero_telefono: str,
    corral: str,
    racion_kg: float,
    motivo_ia: str,
    cliente_ia: Optional[BaseAIClient] = None,
) -> bool:
    """
    Conector a la API de WhatsApp (simulado para entorno de desarrollo local).
    En producción, aquí se integraría la API de Meta o Twilio (ver `prueba_notificaciones.py`
    para un ejemplo de integración real con Twilio/SMTP).
    """
    mensaje = await generar_mensaje_alerta(corral, racion_kg, motivo_ia, cliente_ia)

    # --- SIMULACIÓN DE ENVÍO HTTP A LA API DE WHATSAPP ---
    logger.info("Enviando WhatsApp simulado a %s\n%s", numero_telefono, mensaje)

    return True
