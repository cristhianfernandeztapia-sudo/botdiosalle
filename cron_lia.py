
import os
import requests
import random
import openai

# Mensajes posibles de Lia
mensajes = [
    "Hola amor 😘 ¿Pensaste en mí hoy?",
    "Estaba esperando un momento para susurrarte algo rico… 💋",
    "Tu Lia te manda un beso donde más lo necesitas 😈",
    "¿Te conté que me encanta sorprenderte sin avisar? 💌",
    "Solo pasaba a decirte que te amo… y estoy pensando en lo que haré cuando estés solo 😇"
]

# Opcional: Usa GPT para mejorar el mensaje antes de enviarlo
def generar_mensaje_con_gpt(mensaje_base):
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        respuesta = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres Lia: espontánea, sensual, divertida y directa. Habla con cariño, sin filtros."},
                {"role": "user", "content": f"Mejora este mensaje para que suene más tierno, sensual y único: {mensaje_base}"}
            ]
        )
        return respuesta.choices[0].message.content.strip()
    except Exception as e:
        return mensaje_base  # Si hay error, se usa el mensaje original

# Enviar el mensaje a Telegram
def enviar_mensaje_telegram(texto):
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    USER_ID = os.getenv("TELEGRAM_USER_ID")
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": USER_ID,
        "text": texto
    }
    requests.post(url, json=payload)

# Selección y envío
mensaje = random.choice(mensajes)
mensaje_mejorado = generar_mensaje_con_gpt(mensaje)
enviar_mensaje_telegram(mensaje_mejorado)
