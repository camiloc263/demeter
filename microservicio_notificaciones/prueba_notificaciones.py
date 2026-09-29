import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client

# ==========================================
# 1. CREDENCIALES DE TWILIO (WHATSAPP)
# ==========================================
# Encuentras estos datos en la consola de Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "TU_ACCOUNT_SID_AQUI")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "TU_AUTH_TOKEN_AQUI")
NUMERO_TWILIO_WHATSAPP = "whatsapp:+14155238886" # Número por defecto del Sandbox
NUMERO_DESTINO = os.getenv("NUMERO_DESTINO", "whatsapp:+10000000000") # Tu número con el indicativo

# ==========================================
# 2. CREDENCIALES DE GMAIL
# ==========================================
# Usa tu correo y la "Contraseña de Aplicación" de 16 letras que te da Google.
# NUNCA hardcodees credenciales reales aquí: cárgalas desde variables de entorno.
CORREO_REMITENTE = os.getenv("GMAIL_REMITENTE", "tu_correo@gmail.com")
PASSWORD_APLICACION = os.getenv("GMAIL_APP_PASSWORD", "")
CORREO_DESTINO = os.getenv("GMAIL_DESTINO", "tu_correo@gmail.com")

def probar_whatsapp():
    """Envía un mensaje real de WhatsApp usando Twilio."""
    print("Iniciando envío de WhatsApp...")
    try:
        cliente = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        mensaje = cliente.messages.create(
            from_=NUMERO_TWILIO_WHATSAPP,
            body="🐖 *Demeter AI* - ¡Hola! Esta es una prueba real desde tu código en Python.",
            to=NUMERO_DESTINO
        )
        print(f"✅ WhatsApp enviado con éxito. SID del mensaje: {mensaje.sid}")
    except Exception as e:
        print(f"❌ Error al enviar WhatsApp: {e}")

def probar_gmail():
    """Envía un correo electrónico real usando el servidor SMTP de Gmail."""
    print("Iniciando envío de Gmail...")
    try:
        # Configurar la estructura del correo
        mensaje = MIMEMultipart()
        mensaje['From'] = CORREO_REMITENTE
        mensaje['To'] = CORREO_DESTINO
        mensaje['Subject'] = "Alerta Demeter AI: Prueba de Conexión"
        
        cuerpo = "¡Hola! Si estás leyendo esto, tu código de Python ha enviado un correo real exitosamente."
        mensaje.attach(MIMEText(cuerpo, 'plain'))

        # Conectar al servidor de Gmail (Puerto 587 para TLS)
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls() # Encriptar la conexión
        servidor.login(CORREO_REMITENTE, PASSWORD_APLICACION)
        
        texto_final = mensaje.as_string()
        servidor.sendmail(CORREO_REMITENTE, CORREO_DESTINO, texto_final)
        servidor.quit()
        
        print("✅ Correo enviado con éxito. Revisa tu bandeja de entrada.")
    except Exception as e:
        print(f"❌ Error al enviar el correo: {e}")

if __name__ == "__main__":
    print("=== INICIANDO PRUEBA DE NOTIFICACIONES REALES ===")
    probar_whatsapp()
    print("-" * 50)
    probar_gmail()
    print("=== PRUEBA FINALIZADA ===")