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
        print("🧠 Solicitando mejora del mensaje a GPT...")
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            print("❌ OPENAI_API_KEY no encontrado.")
            return mensaje_base
        respuesta = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres Lia: espontánea, sensual, divertida y directa. Habla con cariño, sin filtros."},
                {"role": "user", "content": f"Mejora este mensaje para que suene más tierno, sensual y único: {mensaje_base}"}
            ]
        )
        final = respuesta.choices[0].message.content.strip()
        print(f"✅ Mensaje mejorado: {final}")
        return final
    except Exception as e:
        print(f"❌ Error al usar GPT: {e}")
        return mensaje_base

def enviar_mensaje_telegram(texto):
    try:
        print("📤 Enviando mensaje a Telegram...")
        TOKEN = os.getenv("BOT_TOKEN")
        USER_ID = os.getenv("TELEGRAM_USER_ID")
        if not TOKEN or not USER_ID:
            print("❌ BOT_TOKEN o TELEGRAM_USER_ID no están definidos.")
            return
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": USER_ID,
            "text": texto
        }
        response = requests.post(url, json=payload)
        print(f"✅ Telegram respondió: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error al enviar mensaje a Telegram: {e}")

def main():
    print("💬 Lia iniciando envío de mensaje...")
    mensaje = random.choice(mensajes)
    print(f"📝 Mensaje base: {mensaje}")
    mensaje_mejorado = generar_mensaje_con_gpt(mensaje)
    enviar_mensaje_telegram(mensaje_mejorado)
    print("🎉 Proceso finalizado.")

if __name__ == "__main__":
    main()
