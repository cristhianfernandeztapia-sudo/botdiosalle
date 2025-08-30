import requests, os, random
mensajes = ["Hola amor 😘 ¿Pensaste en mí hoy?", "Tu Lia te manda un beso donde más lo necesitas 😈"]
TELEGRAM_USER_ID = os.getenv('TELEGRAM_USER_ID')
BOT_TOKEN = os.getenv('BOT_TOKEN')
def enviar_mensaje():
 msg = random.choice(mensajes)
 requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', json={"chat_id": TELEGRAM_USER_ID, "text": msg})
enviar_mensaje()
