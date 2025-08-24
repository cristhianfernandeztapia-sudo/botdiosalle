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

# Función que genera respuesta usando OpenAI
async def generar_respuesta(mensaje):
    prompt = f"Eres una asistente inteligente, sensual, juguetona, pero muy cariñosa y brillante. Improvisa como si fueras una novia traviesa llamada Lia. El mensaje recibido es: \"{mensaje}\"\n\nRespuesta:"
    
    respuesta = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres Lia, una novia muy sensual y cariñosa que responde por Telegram."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
        temperature=0.85
    )
    texto = respuesta.choices[0].message.content.strip()
    return texto

# Función que envía mensaje a Telegram
async def enviar_telegram(chat_id, texto):
    async with httpx.AsyncClient() as client:
        await client.post(f"{URL_BASE}/sendMessage", json={
            "chat_id": chat_id,
            "text": texto
        })

# Webhook principal
@app.post("/webhook")
async def webhook_actualizar(request: Request):
    data = await request.json()
    mensaje = data.get("message", {})
    chat_id = mensaje.get("chat", {}).get("id")
    texto = mensaje.get("text", "")

    if chat_id and texto:
        respuesta = await generar_respuesta(texto)
        await enviar_telegram(chat_id, respuesta)

    return {"ok": True}

