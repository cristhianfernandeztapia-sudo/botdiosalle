import os
import random
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse

from estilos import NOMBRE, EMOJI, SALUDO_START, MENSAJES_BASE_CRON, SYSTEM_LIA
from utils.logger import get_logger
from utils.telegram import send_message, send_audio, set_webhook
from utils.gpt import completar  # ← usamos el motor nuevo

# Flags / ENV
SEND_AUDIO = os.getenv("SEND_AUDIO", "false").lower() == "true"
BASE_URL = os.getenv("BASE_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Afinado (opcionales)
LIA_TEMP = float(os.getenv("LIA_TEMP", "1.10"))
LIA_TOP_P = float(os.getenv("LIA_TOP_P", "0.95"))
LIA_MAX_TOKENS = int(os.getenv("LIA_MAX_TOKENS", "900"))

log = get_logger("main")
app = FastAPI(title="BotLia")

@app.get("/health")
async def health():
    return {"ok": True}

@app.get("/")
async def root():
    return PlainTextResponse("BotLia up")

@app.on_event("startup")
async def startup():
    if BOT_TOKEN and BASE_URL and WEBHOOK_SECRET:
        try:
            await set_webhook(BASE_URL, WEBHOOK_SECRET)
        except Exception as e:
            log.warning(f"No se pudo fijar el webhook en startup: {e}")

@app.get("/set_webhook")
async def set_webhook_route():
    if not (BOT_TOKEN and BASE_URL and WEBHOOK_SECRET):
        raise HTTPException(400, "Faltan variables: BOT_TOKEN, BASE_URL o WEBHOOK_SECRET")
    data = await set_webhook(BASE_URL, WEBHOOK_SECRET)
    return JSONResponse(data)

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    # Seguridad básica: validar secret header si está definido
    if WEBHOOK_SECRET:
        header_secret = request.headers.get("x-telegram-bot-api-secret-token") or request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if header_secret != WEBHOOK_SECRET:
            raise HTTPException(status_code=401, detail="Secret inválido")

    update = await request.json()
    log.debug(f"Update: {update}")

    message = update.get("message") or update.get("edited_message") or {}
    if not message:
        return {"ok": True}

    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = message.get("text") or message.get("caption") or ""
    if not chat_id:
        return {"ok": True}

    # /start
    if text.strip().lower().startswith("/start"):
        saludo = SALUDO_START.format(nombre=NOMBRE, emoji=EMOJI)
        await send_message(chat_id, saludo)
        if SEND_AUDIO and os.getenv("ELEVEN_API_KEY"):
            try:
                from voz_lia import sintetizar
                audio = await sintetizar(saludo)
                await send_audio(chat_id, audio, filename="bienvenida.mp3")
            except Exception as e:
                log.warning(f"Error TTS bienvenida: {e}")
        return {"ok": True}

    # Respuesta creativa (LM Studio vía completar)
    prompt = text.strip() or random.choice(MENSAJES_BASE_CRON)
    try:
        respuesta = completar(
            texto=prompt,
            system_prompt=SYSTEM_LIA,
            temp=LIA_TEMP,
            max_tokens=LIA_MAX_TOKENS,
            top_p=LIA_TOP_P,
        )
    except Exception as e:
        log.warning(f"Error LLM: {e}")
        respuesta = random.choice(MENSAJES_BASE_CRON)

    await send_message(chat_id, respuesta)

    if SEND_AUDIO and os.getenv("ELEVEN_API_KEY"):
        try:
            from voz_lia import sintetizar
            audio = await sintetizar(respuesta)
            await send_audio(chat_id, audio, filename="lia.mp3")
        except Exception as e:
            log.warning(f"Error TTS: {e}")

    return {"ok": True}
