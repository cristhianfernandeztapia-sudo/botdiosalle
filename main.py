import os
import requests
from utils import gpt
from utils.estilos import PERSONALIDAD_LIA
from memoria import cargar_memoria, guardar_memoria
from fastapi import FastAPI, Request

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
        return {"ok": False, "error": "usuario no autorizado"}

    if not texto:
        return {"ok": True, "message": "sin texto"}

    # Cargar memoria
    memoria = cargar_memoria(chat_id)
    historial = memoria.get("historial", [])

    # Generar respuesta con historial
    respuesta = gpt.generar_respuesta(texto_usuario=texto, sistema=PERSONALIDAD_LIA, historial=historial)

    # Actualizar memoria
    historial.append({"user": texto, "lia": respuesta})
    memoria["historial"] = historial
    guardar_memoria(chat_id, memoria)

    # Enviar a Telegram
    requests.post(URL_TELEGRAM, json={
        "chat_id": chat_id,
        "text": respuesta,
    })

    return {"ok": True}
