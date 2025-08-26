import os
import random
import asyncio
from estilos import MENSAJES_BASE_CRON, PROMPT_PERSONA
from utils.logger import get_logger
from utils.telegram import send_message, send_audio
from utils.gpt import embellish

log = get_logger("cron")

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")
CRON_SEND_AUDIO = os.getenv("CRON_SEND_AUDIO", "false").lower() == "true"

async def main():
    if not (BOT_TOKEN and TELEGRAM_USER_ID):
        raise RuntimeError("Faltan BOT_TOKEN o TELEGRAM_USER_ID")
    # Mensaje base → opcionalmente embellecido por OpenAI
    base = random.choice(MENSAJES_BASE_CRON)
    texto = embellish(base, persona=PROMPT_PERSONA)
    await send_message(int(TELEGRAM_USER_ID), texto)
    if CRON_SEND_AUDIO and os.getenv("ELEVEN_API_KEY"):
        try:
            from voz_lia import sintetizar
            audio = await sintetizar(texto)
            await send_audio(int(TELEGRAM_USER_ID), audio, filename="cron_lia.mp3")
        except Exception as e:
            log.warning(f"Error TTS en cron: {e}")

if __name__ == "__main__":
    asyncio.run(main())
