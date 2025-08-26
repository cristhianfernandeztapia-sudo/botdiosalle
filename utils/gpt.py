import os
from typing import Optional
from .logger import get_logger

log = get_logger("gpt")

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

def embellish(texto: str, persona: str, model: Optional[str] = None) -> str:
    """Embellece el texto con OpenAI si hay API key; si no, devuelve el original."""
    if not _client:
        return texto
    model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    try:
        # Usamos el cliente v1 con Chat Completions del cliente (no el módulo legacy)
        resp = _client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": persona},
                {"role": "user", "content": texto},
            ],
            temperature=0.85,
            max_tokens=800,
        )
        out = resp.choices[0].message.content.strip()
        return out or texto
    except Exception as e:
        log.warning(f"OpenAI error: {e}")
        return texto
