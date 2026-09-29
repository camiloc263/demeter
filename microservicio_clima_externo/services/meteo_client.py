import requests

def obtener_clima_actual(latitud: float, longitud: float):
    """Consulta la API de Open-Meteo para obtener temperatura y humedad exactas."""
    # Usamos la API pública de Open-Meteo solicitando Temperatura y Humedad Relativa Actual
    url = (f"https://api.open-meteo.com/v1/forecast"
           f"?latitude={latitud}&longitude={longitud}"
           f"&current=temperature_2m,relative_humidity_2m"
           f"&timezone=auto")
    
    try:
        respuesta = requests.get(url, timeout=5)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            return {
                "temperatura_c": datos["current"]["temperature_2m"],
                "humedad_pct": datos["current"]["relative_humidity_2m"]
            }
        else:
            raise Exception(f"La red meteorológica rechazó la conexión (Status: {respuesta.status_code})")
    except Exception as e:
        raise Exception(f"Fallo de conexión satelital: {str(e)}")