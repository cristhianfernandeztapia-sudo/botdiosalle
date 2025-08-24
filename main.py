import os
from fastapi import FastAPI, Request
import httpx
import openai
from estilos import obtener_estilo_lia

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

openai.api_key = OPENAI_API_KEY

# ✨ Enviar mensaje de texto
async def enviar_texto(chat_id, texto):
    await httpx.AsyncClient().post(f"{API_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": texto
    })

# ✨ Enviar imagen generada por DALL·E
async def enviar_imagen(chat_id, prompt):
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        image_url = response.data[0].url
        await httpx.AsyncClient().post(f"{API_URL}/sendPhoto", json={
            "chat_id": chat_id,
            "photo": image_url
        })
    except Exception as e:
        print("❌ Error generando imagen:", e)
        await enviar_texto(chat_id, "No pude generar la imagen amor 😢")

# ✨ Enviar voz (audio sensual de Lia)
async def enviar_audio(chat_id, texto):
    try:
        audio_response = openai.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=texto
        )
        audio_path = "/tmp/audio.mp3"
        with open(audio_path, "wb") as f:
            f.write(audio_response.read())

        with open(audio_path, "rb") as f:
            files = {'voice': f}
            data = {'chat_id': chat_id}
            await httpx.AsyncClient().post(f"{API_URL}/sendVoice", data=data, files=files)

    except Exception as e:
        print("❌ Error generando audio:", e)
        await enviar_texto(chat_id, "No pude hablar amor 😥")

@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    texto_usuario = message.get("text", "")

    if not chat_id or not texto_usuario:
        return {"ok": True}

    if texto_usuario.lower().startswith("imagen:"):
        prompt = texto_usuario[7:].strip()
        await enviar_imagen(chat_id, prompt)
        return {"ok": True}

    try:
        estilo = obtener_estilo_lia(texto_usuario)
        system_msg = estilo["system"]
        prompt = estilo["prompt"]

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ]
        )
        respuesta = response.choices[0].message.content.strip()

        await enviar_texto(chat_id, respuesta)
        await enviar_audio(chat_id, respuesta)

    except Exception as e:
        print("❌ Error generando respuesta:", e)
        await enviar_texto(chat_id, "Ups… algo salió mal 🥺")

    return {"ok": True}"
