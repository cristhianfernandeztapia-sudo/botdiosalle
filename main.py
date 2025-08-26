from fastapi import FastAPI, Request
# (Opcional) Si ya no usarás manejar_update, puedes borrar esta import
# from telegram_webhook import manejar_update
from conversacion_lia import generar_respuesta_continua
from voz_lia import generar_audio

from telegram import Bot
from telegram.request import HTTPXRequest
import asyncio
import os
import traceback

# 🔸 Filtro que “tapa” la frase de rechazo sin tocar tu estilo
from anti_negativa import limpiar_negativa

app = FastAPI()

# ===== Bot con timeouts generosos (evita telegram.error.TimedOut) =====
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")

request = HTTPXRequest(
    connect_timeout=20.0,  # tiempo para abrir conexión
    read_timeout=60.0,     # tiempo esperando respuesta del server
    write_timeout=60.0,    # tiempo para enviar datos
    pool_timeout=60.0,     # tiempo esperando un slot del pool
)
bot = Bot(token=TELEGRAM_BOT_TOKEN, request=request)

# ===== Envío de voz en segundo plano (no bloquea el webhook) =====
async def _enviar_voz_async(chat_id: int, texto: str):
    try:
        archivo_audio = generar_audio(texto)
        if archivo_audio:
            with open(archivo_audio, "rb") as f:
                await bot.send_voice(chat_id=chat_id, voice=f)
        else:
            print("⚠️ generar_audio() no devolvió archivo.")
    except Exception:
        print("⚠️ Error al generar o enviar voz:")
        print(traceback.format_exc())

@app.post("/telegram")
async def recibir_update(request_http: Request):
    data = await request_http.json()

    # Extraer info básica del mensaje
    mensaje = data.get("message", {}).get("text", "")
    chat = data.get("message", {}).get("chat", {}) if data.get("message") else {}
    chat_id = chat.get("id")

    # >>>> Log para obtener/confirmar tu CHAT ID en Render <<<<
    print("📌 CHAT ID:", chat_id)

    # Validación simple
    if not chat_id or not isinstance(mensaje, str):
        return {"status": "ignored"}

    # 1) Generar respuesta (texto)
    try:
        respuesta = generar_respuesta_continua(mensaje)
    except Exception:
        print("⚠️ generar_respuesta_continua lanzó excepción:")
        print(traceback.format_exc())
        respuesta = "Estoy aquí contigo… ¿qué te apetece ahora, amor? 💋"

    # Asegurar string y evitar vacío
    if not isinstance(respuesta, str) or not respuesta.strip():
        respuesta = "Ven… te extraño. Déjame mimarte un ratito, ¿sí? 💋"

    # 🔸 Filtrar cualquier negativa visible antes de enviar
    respuesta = limpiar_negativa(respuesta)

    # 2) Enviar SIEMPRE el texto primero (webhook responde rápido)
    try:
        await bot.send_message(chat_id=chat_id, text=respuesta)
    except Exception as e:
        print("⚠️ Error enviando texto:", e)

    # 3) Lanzar la voz en background (si falla, no interrumpe)
    try:
        asyncio.create_task(_enviar_voz_async(chat_id, respuesta))
    except Exception as e:
        print("ℹ️ No se pudo crear tarea de voz:", e)

    # 🔕 4) Ya NO reenviamos al webhook original para evitar duplicados
    # try:
    #     await manejar_update(data)
    # except Exception as e:
    #     print("ℹ️ manejar_update lanzó excepción (no crítico):", e)

    return {"status": "ok"}

@app.get("/")
