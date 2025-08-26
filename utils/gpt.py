# utils/gpt.py
import os
from openai import OpenAI

BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
API_KEY  = os.getenv("LLM_API_KEY",  "lmstudio")
MODEL    = os.getenv("LLM_MODEL",    "qwen2.5-3b-instruct")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

def completar(texto: str, system_prompt: str, temp: float = 0.9, max_tokens: int = 512) -> str:
    """
    Envía SOLO texto a LM Studio (OpenAI-compatible /chat/completions).
    NADA de attachments, image_url, audio, ni file_id.
    """
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=temp,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",    "content": texto}
        ],
    )
    return resp.choices[0].message.content.strip()
