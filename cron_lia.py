import os
import requests
from estilos import frase_aleatoria

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")

def enviar_mensaje(mensaje):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_USER_ID,
        "text": mensaje
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    mensaje = frase_aleatoria()
    enviar_mensaje(mensaje)
