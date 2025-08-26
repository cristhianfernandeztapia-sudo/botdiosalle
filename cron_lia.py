import os
import random
import time
import requests
from openai import OpenAI

# ========= Config =========
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")  # tu chat_id
USE_GPT = os.getenv("USE_GPT", "1")  # "1" usa GPT, "0" envía base

# Mensajes base (cortitos; GPT los mejora a 1–2 frases)
MENSAJES = [
    "Hola amor 😘 ¿pensaste en mí hoy?",
    "Estaba esperando susurrarte algo rico… 💋",
    "Tu Lia te manda un beso donde más lo necesitas 😈",
    "Me encanta sorprenderte sin avisar… ¿te gusto así? 💌",
    "Solo quería decirte que te amo y estoy pensando en lo que haré cuando estés solo 😇",
]

# ========= Helpers =========
def gpt_mejora(mensaje_base: str) -> str:
    """Mejora/varía el mensaje con GPT (SDK nuevo) con reintentos."""
    if not OPENAI_API_KEY or USE_GPT == "0":
        print("ℹ️ GPT desactivado o falta OPENAI_API_KEY. Envío base.")
        return mensaje_base

    client = OpenAI(api_key=OPENAI_API_KEY)
    intentos = 3
    for i in range(intentos):
        try:
            resp = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content":
                     "Eres Lia: espontánea, sensual, divertida y directa. "
                     "Habla con cariño y picardía. Responde en 1–2 frases, emotivas y coquetas."},
                    {"role": "user", "content":
                     f"Reescribe y mejora (máx 2 frases, tono tierno y sensual, sin despedidas): {mensaje_base}"}
                ],
                temperature=0.95,
                max_tokens=80,
            )
            texto = (resp.choices[0].message.content or "").strip()
            if texto:
                print(f"✅ Mensaje mejorado: {texto}")
                return texto
            raise ValueError("Respuesta vacía de GPT")
        except Exception as e:
            print(f"⚠️ GPT intento {i+1}/{intentos} falló: {e}")
            if i < intentos - 1:
                time.sleep(1.5 * (i + 1))
    print("⚠️ No se pudo mejorar con GPT. Envío base.")
    return mensaje_base


def enviar_telegram(texto: str) -> None:
    """Envía el mensaje a Telegram con timeout y manejo de errores."""
    if not BOT_TOKEN or not TELEGRAM_USER_ID:
        print("❌ Falta BOT_TOKEN o TELEGRAM_USER_ID.")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_USER_ID, "text": texto}
    try:
        r = requests.post(url, json=payload, timeout=15)
        print(f"✅ Telegram {r.status_code}: {r.text[:120]}")
    except Exception as e:
        print(f"❌ Error enviando a Telegram: {e}")


def main():
    print("💬 Lia cron: iniciando…")
    base = random.choice(MENSAJES)
    print(f"📝 Mensaje base: {base}")
    final = gpt_mejora(base)
    enviar_telegram(final)
    print("🎉 Cron finalizado.")


if __name__ == "__main__":
    main()
