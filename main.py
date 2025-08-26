from fastapi import FastAPI, Request
from telegram_webhook import manejar_update
from conversacion_lia import generar_respuesta_continua
from voz_lia import generar_audio

from telegram import Bot
from telegram.request import HTTPXRequest
import asyncio
import os
import traceback

app = FastAPI()

# ===== Bot con timeouts generosos =====
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")

request = HTTPXRequest(
    connect_timeout=20.0,
    read_timeout=60.0,
    write_timeout=60.0,
    pool_timeout=60.0,
)
bot = Bot(token=TELEGRAM_BOT_TOKEN, request=request)

# ===== Envío de voz en segundo plano =====
async def _enviar_voz_async(chat_id: int, texto: str):
    try:
        archivo_audio = generar_audio(texto)
        if archivo_audio:
            with open(archivo_audio, "rb") as f:
                await bot.send_voice(chat_id=chat_id, voice=f)
        else:
            print("⚠️ generar_audio() no devolvió archivo.")
    except Exception as e:
        print("⚠️ Error al generar o enviar voz:")
        print(traceback.format_exc())

@app.post("/telegram")
async def recibir_update(request_http: Request):
    data = await request_http.json()

    mensaje = data.get("message", {}).get("text", "")
    chat = data.get("message", {}).get("chat", {}) if data.get("message") else {}
    chat_id = chat.get("id")

    if not chat_id or not isinstance(mensaje, str):
        return {"status": "ignored"}

    # 1) Generar respuesta (texto)
    respuesta = generar_respuesta_continua(mensaje)

    # 2) Enviar SIEMPRE el texto primero (webhook responde rápido)
    try:
        await bot.send_message(chat_id=chat_id, text=respuesta)
    except Exception as e:
        print("⚠️ Error enviando texto:", e)

    # 3) Lanzar la voz en background (no bloquea el webhook)
    try:
        asyncio.create_task(_enviar_voz_async(chat_id, respuesta))
    except Exception as e:
        print("ℹ️ No se pudo crear tarea de voz:", e)

    # 4) Pasar también el update al webhook original (opcional)
    try:
        await manejar_update(data)
    except Exception as e:
        print("ℹ️ manejar_update lanzó excepción (no crítico):", e)

    return {"status": "ok"}

@app.get("/")
def root():
    return {"mensaje": "Lia está viva, con voz, y más pícara que nunca en Telegram 😈🎤"}
