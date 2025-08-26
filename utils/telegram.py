import os
import httpx
from typing import Optional
from .logger import get_logger

log = get_logger("telegram")

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    log.warning("BOT_TOKEN no está definido. utils.telegram no podrá enviar mensajes.")
API = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else None

async def send_message(chat_id: int, text: str, parse_mode: str = "HTML"):
    if not API:
        raise RuntimeError("BOT_TOKEN no configurado.")
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(f"{API}/sendMessage", data={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        })
        r.raise_for_status()
        data = r.json()
        log.debug(f"sendMessage: {data}")
        return data

async def send_audio(chat_id: int, audio_bytes: bytes, filename: str = "voz_lia.mp3", caption: Optional[str] = None):
    if not API:
        raise RuntimeError("BOT_TOKEN no configurado.")
    files = {"audio": (filename, audio_bytes, "audio/mpeg")}
    data = {"chat_id": chat_id}
    if caption:
        data["caption"] = caption
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{API}/sendAudio", data=data, files=files)
        r.raise_for_status()
        j = r.json()
        log.debug(f"sendAudio: {j}")
        return j

async def set_webhook(base_url: str, secret: str):
    if not API:
        raise RuntimeError("BOT_TOKEN no configurado.")
    webhook_url = base_url.rstrip('/') + "/telegram/webhook"
    payload = {
        "url": webhook_url,
        "secret_token": secret,
        "max_connections": 5,
        "drop_pending_updates": True
    }
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(f"{API}/setWebhook", data=payload)
        r.raise_for_status()
        j = r.json()
        log.info(f"Webhook fijado en {webhook_url}: {j}")
        return j
