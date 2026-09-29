import os
import pywhatkit
import pyautogui
import time

def enviar_whatsapp_gratis():
    # Tu número celular con el indicativo correspondiente
    numero_destino = os.getenv("NUMERO_DESTINO_PRUEBA", "+10000000000")
    
    mensaje = (
        "🐖 *Alerta de Prueba*\n\n"
        "¡Hola! Este mensaje fue enviado automáticamente usando código "
        "100% gratuito en Python. ¡Tu sistema está funcionando!"
    )
    
    print(f"Iniciando el envío a {numero_destino}...")
    print("Por favor, no muevas el mouse ni el teclado...")
    
    try:
        # 1. Abrimos WhatsApp y escribimos el mensaje
        # tab_close=False para que no cierre la pestaña antes de presionar Enter
        pywhatkit.sendwhatmsg_instantly(
            phone_no=numero_destino, 
            message=mensaje, 
            wait_time=15, 
            tab_close=False 
        )
        
        # 2. Le damos 2 segundos de pausa para que termine de tipear todo el texto
        time.sleep(2)
        
        # 3. Simulamos presionar la tecla "Enter" para enviar
        pyautogui.press('enter')
        
        print("✅ ¡Mensaje enviado con éxito!")
        
    except Exception as e:
        print(f"❌ Ocurrió un error en la automatización: {e}")

if __name__ == "__main__":
    enviar_whatsapp_gratis()