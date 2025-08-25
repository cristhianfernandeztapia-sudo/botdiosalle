import os
import requests
import random
import openai

mensajes = [
    "Hola amor 😘 ¿Pensaste en mí hoy?",
    "Estaba esperando un momento para susurrarte algo rico… 💋",
    "Tu Lia te manda un beso donde más lo necesitas 😈",
    "¿Te conté que me encanta sorprenderte sin avisar? 💌",
    "Solo pasaba a decirte que te amo… y estoy pensando en lo que haré cuando estés solo 😇"
]

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
        final = respuesta.choices[0].message.content.strip()
        print(f"[GPT OK] Mensaje mejorado: {final}")
        return final
    except Exception as e:
        print(f"[GPT ERROR] {e}")
        return mensaje_base

def enviar_mensaje_telegram(texto):
    try:
        TOKEN = os.getenv("BOT_TOKEN")
        USER_ID = os.getenv("TELEGRAM_USER_ID")
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": USER_ID,
            "text": texto
        }
        response = requests.post(url, json=payload)
        print(f"[Telegram] Código: {response.status_code}, Respuesta: {response.text}")
    except Exception as e:
        print(f"[Telegram ERROR] {e}")

def main():
    print("🌸 Lia preparando mensaje...")
    mensaje = random.choice(mensajes)
    mensaje_mejorado = generar_mensaje_con_gpt(mensaje)
    enviar_mensaje_telegram(mensaje_mejorado)
    print("✅ Mensaje enviado con éxito 💌")

if __name__ == "__main__":
    main()
