from fastapi import FastAPI, Request
from telegram_webhook import manejar_update
from conversacion_lia import generar_respuesta_continua

app = FastAPI()

@app.post("/telegram")
async def recibir_update(request: Request):
    data = await request.json()
    await manejar_update(data)
    return {"status": "ok"}

@app.get("/")
def root():
    return {"mensaje": "Lia está viva y con voz en Telegram 😈🎤"}