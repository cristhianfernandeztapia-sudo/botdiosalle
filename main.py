import os
import openai
from fastapi import FastAPI, Request
import httpx
from estilos import obtener_estilo_lia
from voz_lia import generar_audio_lia

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
SEND_MSG_URL = f"{API_URL}/sendMessage"
SEND_AUDIO_URL = f"{API_URL}/sendVoice"

@app.post("/")
async def telegram_webhook(request: Request):
    data = await request.json()
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    user_message = message.get("text", "")

    if not chat_id or not user_message:
        return {"ok": True}

    try:
        # 🔥 Estilo dinámico según el mensaje
        estilo = obtener_estilo_lia(user_message)
        system_message = estilo["system"]
        prompt = estilo["prompt"]

        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        )
        reply = response.choices[0].message.content.strip()

        # Enviar respuesta escrita
        async with httpx.AsyncClient() as async_client:
            await async_client.post(SEND_MSG_URL, json={
                "chat_id": chat_id,
                "text": reply
            })

        # 🎤 Generar audio con voz sensual
        audio_path = generar_audio_lia(reply)
        if audio_path:
            with open(audio_path, "rb") as audio_file:
                files = {"voice": audio_file}
                data = {"chat_id": chat_id}
                await async_client.post(SEND_AUDIO_URL, data=data, files=files)

    except Exception as e:
        print(f"❌ Error generando respuesta: {e}")
        async with httpx.AsyncClient() as async_client:
            await async_client.post(SEND_MSG_URL, json={
                "chat_id": chat_id,
                "text": "Ups… hubo un error generando la respuesta 😔"
            })

    return {"ok": True}
