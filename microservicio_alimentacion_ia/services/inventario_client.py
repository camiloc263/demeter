import os

import requests
from fastapi import HTTPException

# microservicio_inventario corre en el puerto 8003 (ver microservicio_inventario/main.py y .env)
INVENTARIO_URL = os.getenv("INVENTORY_URL", "http://127.0.0.1:8003").rstrip("/")


def verificar_cerdo_en_corral(corral: str, id_cerdo_rfid: str) -> None:
    """
    Verifica contra el Inventario que el corral exista y que el cerdo con
    etiqueta == id_cerdo_rfid esté efectivamente asignado a ese corral, antes
    de aceptar un evento de comedero RFID.
    """
    try:
        respuesta = requests.get(f"{INVENTARIO_URL}/cerdos/", params={"corral": corral}, timeout=5)
    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=503,
            detail="El servicio de Inventario está fuera de línea. No se puede validar el RFID.",
        )

    if respuesta.status_code != 200:
        raise HTTPException(status_code=502, detail="Error de comunicación con el servicio de Inventario.")

    cerdos_en_corral = respuesta.json()
    if not any(c.get("etiqueta") == id_cerdo_rfid for c in cerdos_en_corral):
        raise HTTPException(
            status_code=404,
            detail=f"El RFID '{id_cerdo_rfid}' no corresponde a ningún cerdo registrado en el corral '{corral}'.",
        )
