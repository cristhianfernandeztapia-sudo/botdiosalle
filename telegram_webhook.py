import os
import requests
from conversacion_lia import generar_respuesta_continua
from voz_lia import generar_audio

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

async def manejar_update(data):
    try:
        mensaje = data.get("message") or data.get("edited_message")
        if not mensaje:
            return

        chat_id = mensaje["chat"]["id"]
        texto = mensaje.get("text", "")

        respuesta = generar_respuesta_continua(texto)

        if "!vozON" in texto:
            audio_path = generar_audio(respuesta)
            if audio_path:
                with open(audio_path, "rb") as f:
                    requests.post(
                        f"{TELEGRAM_API_URL}/sendVoice",
                        data={"chat_id": chat_id},
                        files={"voice": f}
                    )
                    os.remove(audio_path)
        else:
            requests.post(
                f"{TELEGRAM_API_URL}/sendMessage",
                json={"chat_id": chat_id, "text": respuesta}
            )

    except Exception as e:
        print(f"Error en manejo de update: {e}")