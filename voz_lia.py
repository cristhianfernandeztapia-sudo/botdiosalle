import os
import httpx
from utils.logger import get_logger

log = get_logger("voz_lia")

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
DEFAULT_VOICE_ID = os.getenv("ELEVEN_VOICE_ID", "XB0fDUnXU5powFXDhCwa")  # Carlota
DEFAULT_MODEL_ID = os.getenv("ELEVEN_MODEL_ID", "eleven_multilingual_v2")

async def sintetizar(texto: str) -> bytes:
    if not ELEVEN_API_KEY:
        raise RuntimeError("ELEVEN_API_KEY no configurada.")
    voice_id = DEFAULT_VOICE_ID
    model_id = DEFAULT_MODEL_ID
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "text": texto,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.85,
            "style": 0.75,
            "use_speaker_boost": True
        }
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, headers=headers, json=body)
        r.raise_for_status()
        audio = r.content
        log.debug(f"TTS generado: {len(audio)} bytes")
        return audio
