import time
import random
import requests
from datetime import datetime

# La URL de nuestro microservicio IoT
URL_IOT = "http://127.0.0.1:8004/iot/"

# El corral que vamos a monitorear
CORRAL_OBJETIVO = "Corral Inexistente 99"

print(f"📡 Iniciando Sensor Virtual para: {CORRAL_OBJETIVO}")
print("Presiona Ctrl+C para detener el sensor...\n")

try:
    while True:
        # 1. Simulamos la lectura de los sensores físicos
        # Maternidad suele estar entre 28 y 32 grados
        temp_simulada = round(random.uniform(28.0, 33.0), 1) 
        # Humedad entre 50% y 70%
        hum_simulada = round(random.uniform(50.0, 70.0), 1)  
        
        # 2. Empaquetamos el dato como si fuera el JSON de Postman
        payload = {
            "corral": CORRAL_OBJETIVO,
            "temperatura_c": temp_simulada,
            "humedad_pct": hum_simulada
        }
        
        # 3. Disparamos el dato hacia nuestro microservicio
        respuesta = requests.post(URL_IOT, json=payload)
        
        # 4. Imprimimos el resultado en pantalla (efecto Matrix)
        hora_actual = datetime.now().strftime("%H:%M:%S")
        if respuesta.status_code == 200:
            print(f"[{hora_actual}] ✅ Éxito -> Temp: {temp_simulada}°C | Humedad: {hum_simulada}%")
        else:
            print(f"[{hora_actual}] ❌ Error del servidor: {respuesta.text}")
            
        # 5. El sensor "duerme" 3 segundos antes de la siguiente lectura
        time.sleep(3)

except KeyboardInterrupt:
    print("\n🛑 Sensor apagado por el usuario. ¡Buen trabajo!")