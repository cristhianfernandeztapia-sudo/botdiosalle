from fastapi import FastAPI, Request
from telegram_webhook import manejar_update
from conversacion_lia import generar_respuesta_continua
from voz_lia import generar_audio

from telegram import Bot
import os
import traceback

app = FastAPI()

# Inicializar el bot de Telegram con el token desde variables de entorno
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TELEGRAM_BOT_TOKEN)

@app.post("/telegram")
async def recibir_update(request: Request):
    data = await request.json()

    # Extraer info básica del mensaje
    mensaje = data.get("message", {}).get("text", "")
    chat_id = data.get("message", {}).get("chat", {}).get("id")

    # Si no hay chat_id o mensaje, ignoramos
    if not chat_id or not isinstance(mensaje, str):
        return {"status": "ignored"}

    # 1) Generar respuesta de Lia
    respuesta = generar_respuesta_continua(mensaje)

    # 2) Enviar SIEMPRE el texto primero
    try:
        await bot.send_message(chat_id=chat_id, text=respuesta)
    except Exception as e:
        print(f"⚠️ Error enviando texto: {e}")

    # 3) Intentar la voz SIN bloquear la respuesta
    try:
        archivo_audio = generar_audio(respuesta)
        if archivo_audio:
            with open(archivo_audio, "rb") as f:
                await bot.send_voice(chat_id=chat_id, voice=f)
        else:
            print("⚠️ generar_audio() no devolvió archivo.")
    except Exception as e:
        print("⚠️ Error al generar o enviar voz:")
        print(traceback.format_exc())

    # 4) Pasar también el update al webhook original, si lo necesitas
    try:
        await manejar_update(data)
    except Exception as e:
        print(f"ℹ️ manejar_update lanzó excepción (no crítico): {e}")

    return {"status": "ok"}

@app.get("/")
def root():
    return {"mensaje": "Lia está viva, con voz, y más pícara que nunca en Telegram 😈🎤"}
