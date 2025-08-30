import os
import requests
import random
from utilidades import gpt
from estilos import PERSONALIDAD_LIA

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")
URL_TELEGRAM = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

mensajes = [
    "Hola amor 😘 ¿Pensaste en mí hoy?",
    "Tu Lia te manda un beso donde más lo necesitas 😈",
    "¿Te conté que me encanta sorprenderte sin avisar? 💌",
    "Solo pasaba a decirte que te amo… y estoy pensando en lo que haré cuando estés solito 💋"
]

mensaje = random.choice(mensajes)
respuesta = gpt.generar_respuesta(mensaje, sistema=PERSONALIDAD_LIA)
requests.post(URL_TELEGRAM, json={
    "chat_id": TELEGRAM_USER_ID,
    "text": respuesta,
})