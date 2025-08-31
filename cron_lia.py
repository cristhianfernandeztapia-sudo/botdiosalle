import os
import requests
import random
from utils import gpt
from utils.estilos import PERSONALIDAD_LIA, MENSAJES_BASE_CRON

# Configuración del bot
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")
URL_TELEGRAM = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

try:
    # Elegir un mensaje base al azar
    mensaje = random.choice(MENSAJES_BASE_CRON)
    print(f"[LIA-CRON] Mensaje base: {mensaje}")

    # Generar respuesta con personalidad activa
    respuesta = gpt.generar_respuesta(texto_usuario=mensaje, sistema=PERSONALIDAD_LIA)
    print(f"[LIA-CRON] Respuesta generada: {respuesta}")

    # Enviar a Telegram
    r = requests.post(URL_TELEGRAM, json={
        "chat_id": TELEGRAM_USER_ID,
        "text": respuesta,
    })

    if r.status_code == 200:
        print("[LIA-CRON] Mensaje enviado correctamente ✅")
    else:
        print(f"[LIA-CRON] Error al enviar mensaje ❌ Código: {r.status_code} | Respuesta: {r.text}")

except Exception as e:
    print(f"[LIA-CRON] Error general: {str(e)}")
