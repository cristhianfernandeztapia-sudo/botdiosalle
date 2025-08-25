import requests
import os

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = "XB0fDUnXU5powFXDhCwa"  # Carlota

def generar_audio(texto: str) -> str:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "text": texto,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.40,
            "similarity_boost": 0.85,
            "style": 0.75,
            "use_speaker_boost": True
        }
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        with open("voz_lia.mp3", "wb") as f:
            f.write(response.content)
        return "voz_lia.mp3"
    else:
        print(f"Error al generar audio: {response.status_code}, {response.text}")
        return None
