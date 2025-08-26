from fastapi import FastAPI, Request
from conversacion_lia import generar_respuesta_continua
from voz_lia import generar_audio

from telegram import Bot
from telegram.request import HTTPXRequest
import asyncio, os, traceback
from datetime import datetime

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DEBUG = os.getenv("DEBUG_LIA", "false").lower() in ("1", "true", "yes")

request = HTTPXRequest(
    connect_timeout=20.0,
    read_timeout=60.0,
    write_timeout=60.0,
    pool_timeout=60.0,
)
bot = Bot(token=BOT_TOKEN, request=request)

def _ts() -> str:
    return datetime.utcnow().strftime("%H:%M:%S")

async def _enviar_voz_async(chat_id: int, texto: str):
    try:
        archivo = generar_audio(texto)
        if archivo:
            with open(archivo, "rb") as f:
                await bot.send_voice(chat_id=chat_id, voice=f)
        elif DEBUG:
            print(f"[{_ts()} VOZ] generar_audio() no devolvió archivo")
    except Exception:
        print(f"[{_ts()} VOZ] Error enviando voz:\n{traceback.format_exc()}")

@app.post("/telegram")
async def recibir_update(req: Request):
    data = await req.json()
    msg = data.get("message", {}).get("text", "")
    chat = data.get("message", {}).get("chat", {}) if data.get("message") else {}
    chat_id = chat.get("id")
    if DEBUG: print(f"[{_ts()} WEBHOOK] chat_id={chat_id} msg={repr(msg)[:160]}")

    if not chat_id or not isinstance(msg, str):
        return {"status": "ignored"}

    # 100% tu estilos.py
    try:
        texto = generar_respuesta_continua(msg)
    except Exception:
        print(f"[{_ts()} MAIN] Error generar_respuesta:\n{traceback.format_exc()}")
        texto = "Amor, se me cruzó un cable. Dímelo otra vez y sigo. 💗"

    if DEBUG: print(f"[{_ts()} MAIN] RESP_FINAL len={len(texto)}")

    # Enviar TODO el texto (sin recortes ni filtros)
    try:
        await bot.send_message(chat_id=chat_id, text=texto)
    except Exception as e:
        print(f"[{_ts()} MAIN] Error enviando texto: {e}")

    # Voz en segundo plano
    try:
        asyncio.create_task(_enviar_voz_async(chat_id, texto))
    except Exception as e:
        print(f"[{_ts()} MAIN] No pude crear tarea de voz: {e}")

    return {"status": "ok"}

@app.get("/")
def root():
    return {"mensaje": "Lia online. Estilo directo desde estilos.py 😈🎤"}
