from fastapi import FastAPI, Request
from telegram_webhook import manejar_update
from conversacion_lia import generar_respuesta_continua
from voz_lia import generar_audio

from telegram import Bot
import os

app = FastAPI()

# Inicializar el bot de Telegram con el token desde variables de entorno
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TELEGRAM_BOT_TOKEN)

@app.post("/telegram")
async def recibir_update(request: Request):
    data = await request.json()

    # Extraer info básica del mensaje
    mensaje = data.get("message", {}).get("text")
    chat_id = data.get("message", {}).get("chat", {}).get("id")

    if mensaje and chat_id:
        # Generar respuesta de Lia
        respuesta = generar_respuesta_continua(mensaje)

        # ✨ Generar audio con estilo automático (voz Carlota)
        try:
            archivo_audio = generar_audio(respuesta)
            if archivo_audio:
                with open(archivo_audio, "rb") as f:
                    await bot.send_voice(chat_id=chat_id, voice=f)
        except Exception as e:
            # Si hay error con el audio, seguimos con texto
            print(f"Error al generar o enviar voz: {e}")

        # 📤 Enviar también el texto
        await bot.send_message(chat_id=chat_id, text=respuesta)

    # Pasar también el update al webhook original si necesitas mantenerlo
    await manejar_update(data)
    return {"status": "ok"}

@app.get("/")
def root():
    return {"mensaje": "Lia está viva, con voz, y más pícara que nunca en Telegram 😈🎤"}
