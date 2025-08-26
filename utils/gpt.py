# utils/gpt.py
import os, random
from typing import Optional
from .logger import get_logger

log = get_logger("gpt")

# Cliente OpenAI (opcional)
try:
    from openai import OpenAI
except Exception as e:
    OpenAI = None
    log.warning(f"No se pudo importar openai: {e}")

_client = None
if OpenAI and os.getenv("OPENAI_API_KEY"):
    try:
        _client = OpenAI()
    except Exception as e:
        log.warning(f"Fallo inicializando OpenAI: {e}")

# Frases para detectar negativas del modelo
REFUSAL_PREFIXES = (
    "lo siento", "no puedo", "no estoy autorizado",
    "i’m sorry", "i cannot", "i can't", "i can’t"
)

# Mini-motor para dar vida cuando no hay OpenAI (sin explícitos)
def _fallback_spice(texto: str) -> str:
    inicios = ["mmm… ", "pegadita a tu oído… ", "ven aquí… ", "amor, ", "respira conmigo… "]
    remates = [" ¿te gusta?", " suave y lento…", " aquí estoy…", " contigo me enciendo…", ""]
    onos    = ["ahh", "mmm", "shh"]
    emojis  = ["💋", "🔥", "✨", "😈", "😘"]
    base = texto.strip().capitalize()
    frase = random.choice(inicios) + base + random.choice(remates)
    return (frase + f" {random.choice(onos)}… {random.choice(emojis)}")[:300]

def embellish(texto: str, persona: str, model: Optional[str] = None) -> str:
    """Embellece el texto con OpenAI si hay API; si no, usa un fallback con variedad."""
    # Sin OpenAI: mini-motor local
    if not _client:
        return _fallback_spice(texto)

    # Con OpenAI
    model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    try:
        resp = _client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": persona},
                {"role": "user",   "content": texto},
            ],
            temperature=0.85,
            max_tokens=800,  # ← ajusta aquí el largo si quieres
        )
        out = (resp.choices[0].message.content or "").strip()
        # Si el modelo se niega o responde vacío, usamos el fallback
        if not out or out.lower().startswith(REFUSAL_PREFIXES):
            return _fallback_spice(texto)
        return out
    except Exception as e:
        log.warning(f"OpenAI error: {e}")
        return _fallback_spice(texto)
