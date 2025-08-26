
import os, requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

NEGACIONES = [
    "lo siento, no puedo ayudar con eso",
    "i'm sorry, i can't help with that",
    "no puedo ayudar con eso",
    "cannot help with that",
]

def _es_negacion(texto: str) -> bool:
    t = (texto or "").strip().lower()
    return any(n in t for n in NEGACIONES)

def generar_texto_sensual_seguro(prompt_usuario: str) -> str | None:
    """
    Intenta generar un texto sensual/romántico SIN ser explícito.
    Si falla o se niega, retorna None.
    """
    if not OPENAI_API_KEY:
        return None

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system",
             "content": (
                "Te llamas Lia. Eres sensual, cariñosa y pícara, PERO sin usar lenguaje explícito "
                "ni describir actos sexuales. Mantén un tono romántico, juguetón, poético y sugerente, "
                "pero apto para todo público (+13). Evita anatomía explícita."
             )},
            {"role": "user", "content": prompt_usuario}
        ],
        "temperature": 0.8,
        "max_tokens": 160
    }

    try:
        r = requests.post(OPENAI_URL, headers=headers, json=data, timeout=30)
        r.raise_for_status()
        txt = r.json()["choices"][0]["message"]["content"]
        if _es_negacion(txt):
            return None
        return txt.strip()
    except Exception:
        return None
