import requests
from fastapi import HTTPException

# URL del Microservicio de Corrales
CORRALES_SERVICE_URL = "http://127.0.0.1:8002/corrales/"

def verificar_corral_existe(nombre_corral: str):
    """Consulta al Microservicio de Corrales (puerto 8002) para verificar la existencia del corral."""
    try:
        respuesta = requests.get(CORRALES_SERVICE_URL, timeout=3.0)
        
        if respuesta.status_code == 200:
            corrales = respuesta.json()
            # Buscamos si el corral está registrado
            corral_encontrado = next((c for c in corrales if c["nombre"] == nombre_corral), None)
            
            if not corral_encontrado:
                raise HTTPException(
                    status_code=400,
                    detail=f"Operación rechazada: El corral '{nombre_corral}' no está registrado en la granja."
                )
            return corral_encontrado
        else:
            raise HTTPException(
                status_code=503,
                detail="No se pudo obtener la lista de corrales desde el servicio correspondiente."
            )
            
    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=503,
            detail="Error de comunicación: El Microservicio de Corrales (puerto 8002) está fuera de línea."
        )