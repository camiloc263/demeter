import requests
from fastapi import HTTPException

CORRALES_URL = "http://127.0.0.1:8002"

def verificar_corral_existe(nombre_corral: str):
    try:
        respuesta = requests.get(f"{CORRALES_URL}/corrales/{nombre_corral}")
        
        if respuesta.status_code == 404:
            raise HTTPException(
                status_code=404, 
                detail=f"Operación cancelada: El '{nombre_corral}' no ha sido construido."
            )
        elif respuesta.status_code != 200:
            raise HTTPException(status_code=502, detail="Error al consultar el servicio de Corrales.")
            
        # 👇 CAMBIO CLAVE: Ahora devolvemos el JSON con los datos del corral
        return respuesta.json() 

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503, 
            detail="El servicio de Corrales está apagado."
        )