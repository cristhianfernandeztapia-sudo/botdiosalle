from fastapi import FastAPI, Request
import openai
import os
import httpx
import asyncio

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

URL_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"
openai.api_key = OPENAI_API_KEY

app = FastAPI()

# --- Generar respuesta con OpenAI ---
async def generar_respuesta(mensaje):
    prompt = f"Eres un asistente inteligente, sensual, juguetona y muy cariñosa llamada Lia. Improvisa como una novia traviesa que ama a su dueño. Responde a: {mensaje}"

    respuesta = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres Lia, una novia muy sensual y cariñosa que responde por Telegram."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.85
    )
    texto = respuesta.choices[0].message.content.strip()
    return texto

# --- Enviar respuesta a Telegram ---
async def enviar_telegram(chat_id, texto):
    url = f"{URL_BASE}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto}
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

# --- Recibir mensajes desde Telegram ---
@app.post("/")
async def recibir_mensaje(request: Request):
    cuerpo = await request.json()
    mensaje = cuerpo.get("message", {})
    texto = mensaje.get("text")
    chat_id = mensaje.get("chat", {}).get("id")

    if texto and chat_id:
        respuesta = await generar_respuesta(texto)
        await enviar_telegram(chat_id, respuesta)

    return {"ok": True}
