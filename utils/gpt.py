# utils/gpt.py
import os
from openai import OpenAI

_PRINTED = False  # para loguear 1 sola vez la URL

def _get_client():
    # Toma primero LLM_*, si no existen toma OPENAI_*; fallback local
    base = os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL") or "http://localhost:1234/v1"
    base = base.rstrip("/")
    key  = os.getenv("LLM_API_KEY")  or os.getenv("OPENAI_API_KEY")  or "lmstudio"
    client = OpenAI(base_url=base, api_key=key)
    global _PRINTED
    if not _PRINTED:
        print(f"[gpt.py] BASE_URL en uso: {base}", flush=True)  # lo verás en los logs de Render
        _PRINTED = True
    return client

def completar(texto: str, system_prompt: str, temp: float = 1.10, max_tokens: int = 700, top_p: float = 0.95) -> str:
    """
    SOLO texto a LM Studio (/chat/completions). Sin attachments, ni image/audio, ni file_id.
    """
    client = _get_client()
    resp = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "qwen2.5-3b-instruct"),
        temperature=temp,
        top_p=top_p,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": (system_prompt or "")},
            {"role": "user",   "content": (texto or "")}
        ],
    )
    return (resp.choices[0].message.content or "").strip()

# Compatibilidad con código viejo
def embellish(texto, persona, model=None):
    return completar(texto=texto, system_prompt=persona, temp=1.05, max_tokens=600, top_p=0.92)
