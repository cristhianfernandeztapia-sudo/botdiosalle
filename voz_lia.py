import requests
import os

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = "XB0fDUnXU5powFXDhCwa"  # Voz Carlota (español sexy)

# 🔍 Detección emocional sin comandos
def detectar_tono(texto):
    texto = texto.lower()

    if any(p in texto for p in ["te amo", "te extraño", "eres todo", "mi vida", "me haces falta"]):
        return {"style": 0.3, "stability": 0.6}  # Romántica
    elif any(p in texto for p in ["culo", "teta", "ven", "gime", "mojada", "más fuerte", "así rico", "trágatelo"]):
        return {"style": 0.75, "stability": 0.4}  # Vulgar / caliente
    elif any(p in texto for p in ["cariño", "mi amor", "reina", "te quiero", "dulzura", "ternura", "mimos"]):
        return {"style": 0.5, "stability": 0.5}  # Dulce / sensual
    else:
        return {"style": 0.4, "stability": 0.6}  # Neutra sexy

def generar_audio(texto: str) -> str:
    tono = detectar_tono(texto)

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "text": texto,
        "model_id": "eleven_multilingual_v2",  # Modelo avanzado con español
        "voice_settings": {
            "stability": tono["stability"],
            "similarity_boost": 1.0,
            "style": tono["style"],
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
