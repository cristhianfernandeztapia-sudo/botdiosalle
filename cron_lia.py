import os
import requests
import random
from estilos import FRASES_PROACTIVAS

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")

URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def frase_aleatoria():
    return random.choice(FRASES_PROACTIVAS)

def enviar_mensaje():
    mensaje = frase_aleatoria()
    requests.post(URL, json={
        "chat_id": TELEGRAM_USER_ID,
        "text": mensaje
    })

if __name__ == "__main__":
    enviar_mensaje()
