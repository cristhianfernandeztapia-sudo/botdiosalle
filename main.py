import os
import openai
from fastapi import FastAPI, Request
from utils.gpt import generar_respuesta
import requests

app = FastAPI()
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

def enviar_mensaje(chat_id, texto):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": texto}
    requests.post(url, json=data)

@app.post(f"/{WEBHOOK_SECRET}")
async def recibir_mensaje(request: Request):
    data = await request.json()
    mensaje = data.get("message", {})
    chat_id = str(mensaje.get("chat", {}).get("id"))
    texto_usuario = mensaje.get("text", "")

    if chat_id == TELEGRAM_USER_ID:
        respuesta = generar_respuesta(texto_usuario)
        enviar_mensaje(chat_id, respuesta)
    return {"ok": True}
