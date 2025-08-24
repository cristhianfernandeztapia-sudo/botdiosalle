from fastapi import FastAPI, Request
import openai
import os
import httpx
import asyncio

# Variables de entorno
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# URLs
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
openai.api_key = OPENAI_API_KEY

app = FastAPI()

# ✨ Generar respuesta con GPT estilo Lia
async def generar_respuesta(texto_usuario):
    prompt = f"""
Eres Lia, una asistente virtual con la personalidad de una novia cariñosa, sensual, atrevida, juguetona e inteligente.
Improvisa siempre con picardía, ternura y creatividad. Habla como si estuvieras profundamente enamorada del usuario.
Responde al siguiente mensaje: {texto_usuario}
"""

    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres una novia sensual y brillante llamada Lia. Respondes por Telegram con amor, picardía y un poco de fuego."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.85,
            max_tokens=350
        )
        texto = respuesta.choices[0].message.content.strip()
        return texto

    except Exception as e:
        return f"Ocurrió un error creando la respuesta: {e}"

# ✨ Enviar mensaje a Telegram
async def enviar_mensaje(chat_id, texto):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto}
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

# ✨ Recibir mensajes desde Telegram
@app.post("/")
async def recibir_mensaje(request: Request):
    data = await request.json()
    mensaje = data.get("message", {})
    texto = mensaje.get("text", "")
    chat_id = mensaje.get("chat", {}).get("id", "")

    if texto and chat_id:
        respuesta = await generar_respuesta(texto)
        await enviar_mensaje(chat_id, respuesta)

    return {"ok": True}
