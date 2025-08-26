from fastapi import FastAPI, Request
from conversacion_lia import generar_respuesta_continua
from voz_lia import generar_audio
from anti_negativa import limpiar_negativa

from telegram import Bot
from telegram.request import HTTPXRequest
import asyncio
import os
import traceback
from datetime import datetime

app = FastAPI()

# ===== Configuración general =====
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
DEBUG = os.getenv("DEBUG_LIA", "false").lower() in ("1", "true", "yes")

request = HTTPXRequest(
    connect_timeout=20.0,
    read_timeout=60.0,
    write_timeout=60.0,
    pool_timeout=60.0,
)
bot = Bot(token=TELEGRAM_BOT_TOKEN, request=request)

def _ts():
    """Marca de tiempo para logs"""
    return datetime.utcnow().strftime("%H:%M:%S")

# ===== Enviar voz de forma asíncrona =====
async def _enviar_voz_async(chat_id: int, texto: str):
    try:
        if DEBUG:
            print(f"[{_ts()} VOZ] Generando audio…")
        archivo_audio = generar_audio(texto)
        if archivo_audio:
            with open(archivo_audio, "rb") as f:
                await bot.send_voice(chat_id=chat_id, voice=f)
            if DEBUG:
                print(f"[{_ts()} VOZ] Audio enviado ✅")
        else:
            print(f"[{_ts()} VOZ] ⚠️ generar_audio() no devolvió archivo.")
    except Exception:
        print(f"[{_ts()} VOZ] ⚠️ Error al generar o enviar voz:")
        print(traceback.format_exc())

# ===== Webhook principal =====
@app.post("/telegram")
async def recibir_update(request_http: Request):
    data = await request_http.json()

    mensaje = data.get("message", {}).get("text", "")
    chat = data.get("message", {}).get("chat", {}) if data.get("message") else {}
    chat_id = chat.get("id")

    print(f"[{_ts()} WEBHOOK] chat_id={chat_id} msg={repr(mensaje)[:120]}")

    if not chat_id or not isinstance(mensaje, str):
        return {"status": "ignored"}

    # 1) Generar respuesta
    try:
        respuesta = generar_respuesta_continua(mensaje)
    except Exception:
        print(f"[{_ts()} MAIN] ⚠️ Error en generar_respuesta_continua:")
        print(traceback.format_exc())
        respuesta = "Estoy aquí contigo… ¿qué te apetece ahora, amor? 💋"

    if not isinstance(respuesta, str) or not respuesta.strip():
        respuesta = "Ven… te extraño. Déjame mimarte un ratito, ¿sí? 💋"

    if DEBUG:
        print(f"[{_ts()} MAIN] ➡️ RESP_ORIGINAL: {repr(respuesta)[:600]}")

    # 2) Filtrar frases negativas antes de enviar
    respuesta_filtrada = limpiar_negativa(respuesta)

    if DEBUG:
        print(f"[{_ts()} MAIN] ✅ RESP_ENVIADA : {repr(respuesta_filtrada)[:600]}")

    # 3) Enviar texto primero
    try:
        await bot.send_message(chat_id=chat_id, text=respuesta_filtrada)
    except Exception as e:
        print(f"[{_ts()} MAIN] ⚠️ Error enviando texto: {e}")

    # 4) Lanzar la voz en background
    try:
        asyncio.create_task(_enviar_voz_async(chat_id, respuesta_filtrada))
    except Exception as e:
        print(f"[{_ts()} MAIN] ℹ️ No se pudo crear tarea de voz: {e}")

    return {"status": "ok"}

@app.get("/")
def root():
    return {"mensaje": "Lia está viva, con voz, y más pícara que nunca en Telegram 😈🎤"}
