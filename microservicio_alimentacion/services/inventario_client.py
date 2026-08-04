import requests
from fastapi import HTTPException

# URL base de tu microservicio de Inventario (Puerto 8000)
INVENTARIO_URL = "http://127.0.0.1:8000"

def verificar_corral_existe(nombre_corral: str):
    """
    Se comunica con el microservicio de Inventario para verificar 
    si hay cerdos registrados en un corral específico.
    """
    try:
        # Hacemos la llamada HTTP como si fuéramos Postman
        respuesta = requests.get(f"{INVENTARIO_URL}/cerdos/?corral={nombre_corral}")
        
        # Si el servicio de inventario da un error interno, avisamos
        if respuesta.status_code != 200:
            raise HTTPException(status_code=502, detail="Error de comunicación con el servicio de Inventario.")
        
        # Convertimos la respuesta JSON en una lista de Python
        cerdos_en_corral = respuesta.json()
        
        # Si la lista está vacía, significa que no hay a quién alimentar
        if len(cerdos_en_corral) == 0:
            raise HTTPException(
                status_code=404, 
                detail=f"Operación cancelada: El {nombre_corral} no existe o no tiene cerdos registrados."
            )
            
        return True # Si todo sale bien, la validación pasa

    except requests.exceptions.ConnectionError:
        # Esto ocurre si olvidaste encender el servidor de Inventario
        raise HTTPException(
            status_code=503, 
            detail="El servicio de Inventario está fuera de línea. Enciéndalo para poder registrar alimentos."
        )