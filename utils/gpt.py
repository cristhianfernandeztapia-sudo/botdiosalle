# utils/gpt.py
import os
from openai import OpenAI

# Config desde variables de entorno (LM Studio / túnel)
BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1").rstrip("/")
API_KEY  = os.getenv("LLM_API_KEY",  "lmstudio")
MODEL    = os.getenv("LLM_MODEL",    "qwen2.5-3b-instruct")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

def completar(
    texto: str,
    system_prompt: str,
    temp: float = 1.10,        # un poco más “jugoso”
    max_tokens: int = 900,
    top_p: float = 0.92        # opcional: variedad controlada
) -> str:
    """
    Envía SOLO texto a LM Studio (OpenAI-compatible /chat/completions).
    NADA de attachments, image_url, audio, ni file_id.
    """
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=temp,
        top_p=top_p,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt or ""},
            {"role": "user",   "content": texto or ""}
        ],
    )
    content = ""
    if resp.choices and resp.choices[0].message:
        content = (resp.choices[0].message.content or "").strip()
    return content

# --- Compatibilidad con código viejo ---
def embellish(texto, persona, model=None):
    # Usa el motor nuevo de LM Studio (solo texto)
    return completar(texto=texto, system_prompt=persona, temp=1.05, max_tokens=900, top_p=0.92)
