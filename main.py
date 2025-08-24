import os
import openai
from fastapi import FastAPI, Request
import uvicorn
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
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message.content.strip()

        async with httpx.AsyncClient() as async_client:
            await async_client.post(API_URL, json={
                "chat_id": chat_id,
                "text": reply
            })

    except Exception as e:
        print(f"Error generando respuesta: {e}")
        async with httpx.AsyncClient() as async_client:
            await async_client.post(API_URL, json={
                "chat_id": chat_id,
                "text": "Ocurrió un error al generar la respuesta 😔"
            })

    return {"ok": True}
