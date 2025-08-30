from fastapi import FastAPI, Request
import os
import requests
from utilidades import gpt
from estilos import PERSONALIDAD_LIA

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

URL_TELEGRAM = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

@app.post("/telegram/webhook")
async def recibir_mensaje(request: Request):
    payload = await request.json()
    mensaje = payload.get("message", {})
    texto = mensaje.get("text")
    chat_id = mensaje.get("chat", {}).get("id")

    if str(chat_id) != TELEGRAM_USER_ID:
        print(f"Intento de acceso no autorizado: {chat_id}")
        return {"ok": False, "error": "usuario no autorizado"}

    if not texto:
        print("Mensaje sin texto recibido")
        return {"ok": True, "message": "sin texto"}

    print(f"Mensaje recibido: {texto}")
    respuesta = gpt.generar_respuesta(texto, sistema=PERSONALIDAD_LIA)
    print(f"Respuesta generada: {respuesta}")

    requests.post(URL_TELEGRAM, json={
        "chat_id": chat_id,
        "text": respuesta,
    })

    return {"ok": True}
