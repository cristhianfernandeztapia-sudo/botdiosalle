import requests
import os
import re

ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = "XB0fDUnXU5powFXDhCwa"  # Voz Carlota sensual

# Configuraciones especiales por estilo directo
ESTILOS_DIRECTOS = {
    "susurro": {"stability": 0.20, "style": 1.00},
    "gemido": {"stability": 0.10, "style": 1.00},
    "risa": {"stability": 0.30, "style": 0.90},
    "sumisa": {"stability": 0.50, "style": 0.60},
    "atrevida": {"stability": 0.30, "style": 1.20}
}

# 🔍 Detección de estilo explícito + tono emocional por defecto
def detectar_tono(texto: str) -> dict:
    texto_lower = texto.lower()

    # 1. Detectar estilos explícitos por palabra clave
    if "susurro" in texto_lower:
        return {"estilo": "susurro", "params": ESTILOS_DIRECTOS["susurro"]}
    elif "gemido" in texto_lower:
        return {"estilo": "gemido", "params": ESTILOS_DIRECTOS["gemido"]}
    elif "risa pícara" in texto_lower or "risa" in texto_lower:
        return {"estilo": "risa", "params": ESTILOS_DIRECTOS["risa"]}
    elif "sumisa" in texto_lower:
        return {"estilo": "sumisa", "params": ESTILOS_DIRECTOS["sumisa"]}
    elif "atrevida" in texto_lower:
        return {"estilo": "atrevida", "params": ESTILOS_DIRECTOS["atrevida"]}

    # 2. Si no hay estilo explícito, aplicar detección emocional por contenido
    if any(p in texto_lower for p in ["te amo", "te extraño", "eres todo", "mi vida", "me haces falta"]):
        return {"estilo": "romántica", "params": {"style": 0.3, "stability": 0.6}}
    elif any(p in texto_lower for p in ["culo", "teta", "ven", "gime", "mojada", "más fuerte", "así rico", "trágatelo"]):
        return {"estilo": "vulgar", "params": {"style": 0.75, "stability": 0.4}}
    elif any(p in texto_lower for p in ["cariño", "mi amor", "reina", "te quiero", "dulzura", "ternura", "mimos"]):
        return {"estilo": "dulce", "params": {"style": 0.5, "stability": 0.5}}

    # 3. Por defecto, estilo neutral sensual
    return {"estilo": "normal", "params": {"style": 0.4, "stability": 0.6}}

# ✨ Generador de audio con limpieza del texto si tiene estilo explícito
def generar_audio(texto: str) -> str:
    tono = detectar_tono(texto)
    estilo = tono["estilo"]
    parametros = tono["params"]

    # Eliminar mención del estilo si está en el texto (para que no lo diga en voz)
    if estilo in texto.lower():
        texto = re.sub(fr"(?i)\b{estilo}\b", "", texto).strip()

    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "text": texto,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": parametros["stability"],
            "similarity_boost": 1.0,
            "style": parametros["style"],
            "use_speaker_boost": True
        }
    }

    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        headers=headers,
        json=body
    )

    if response.status_code == 200:
        with open("voz_lia.mp3", "wb") as f:
            f.write(response.content)
        return "voz_lia.mp3"
    else:
        print(f"Error al generar audio: {response.status_code}, {response.text}")
        return None
