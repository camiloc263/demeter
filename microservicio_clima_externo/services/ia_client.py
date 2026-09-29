import os

import requests

URL_IA_BIENESTAR = os.getenv("IA_URL", "http://127.0.0.1:8006").rstrip("/") + "/predecir"

def consultar_ia_bienestar(temperatura_c: float, humedad_pct: float, peso_promedio_kg: float):
    """Pide un diagnóstico al microservicio_ia (puerto 8006) basado en el clima satelital."""
    payload = {
        "temperatura_c": temperatura_c,
        "humedad_pct": humedad_pct,
        "peso_promedio_kg": peso_promedio_kg
    }
    
    try:
        respuesta = requests.post(URL_IA_BIENESTAR, json=payload, timeout=5)
        if respuesta.status_code == 200:
            return respuesta.json()
        else:
            return {
                "estado_codigo": -1,
                "mensaje": f"No se pudo consultar la IA (Status {respuesta.status_code})",
                "certeza_porcentaje": 0.0
            }
    except Exception as e:
        return {
            "estado_codigo": -1,
            "mensaje": f"Error al conectar con el microservicio_ia (8006): {str(e)}",
            "certeza_porcentaje": 0.0
        }