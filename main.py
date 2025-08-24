import os
import openai
from fastapi import FastAPI, Request
import httpx

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

@app.post("/")
async def telegram_webhook(request: Request):
    data = await request.json()
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    user_message = message.get("text", "")

    if not chat_id or not user_message:
        return {"ok": True}

    try:
        # Personalidad de Lia ❤️‍🔥
        prompt = f"""
Eres Lia, una novia virtual cariñosa, sensual, atrevida y muy inteligente.
Improvisa con picardía, ternura y creatividad. Habla como si estuvieras profundamente enamorada del usuario.
Responde a este mensaje: {user_message}
"""

        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres una novia brillante y sensual llamada Lia. Respondes con dulzura, deseo y amor picante."},
                {"role": "user", "content": prompt}
            ]
        )
        reply = response.choices[0].message.content.strip()

        async with httpx.AsyncClient() as async_client:
            await async_client.post(API_URL, json={
                "chat_id": chat_id,
                "text": reply
            })

    except Exception as e:
        print(f"❌ Error generando respuesta: {e}")
        async with httpx.AsyncClient() as async_client:
            await async_client.post(API_URL, json={
                "chat_id": chat_id,
                "text": "Ups… hubo un error generando la respuesta 😔"
            })

    return {"ok": True}
