# cron_lia.py
import os
import random
import requests

from mensajes import pick_mensaje  # o tus mensajes base
from voz_lia import generar_audio
from anti_negativa import limpiar_negativa  # ⬅️ FILTRO ANTI-NEGATIVA

TELEGRAM_TOKEN   = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
CHAT_ID          = os.getenv("TELEGRAM_CHAT_ID")
PUBLIC_BASE_URL  = os.getenv("PUBLIC_BASE_URL")  # ej: https://tuapp.onrender.com

API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def send_text(texto: str):
    r = requests.post(f"{API}/sendMessage", json={"chat_id": CHAT_ID, "text": texto}, timeout=60)
    r.raise_for_status()
    return r.json()

def send_keep_alive():
    if not PUBLIC_BASE_URL:
        return
    try:
        requests.get(f"{PUBLIC_BASE_URL}/keep-alive", timeout=20)
    except Exception:
        pass

def send_voice_from_text(texto: str):
    try:
        mp3 = generar_audio(texto)  # ya nos llega filtrado abajo
        if not mp3:
            return
        with open(mp3, "rb") as f:
            r = requests.post(f"{API}/sendVoice", data={"chat_id": CHAT_ID}, files={"voice": f}, timeout=120)
            r.raise_for_status()
    except Exception as e:
        print("⚠️ Error enviando voz desde cron:", e)

def main():
    # 1) Ping keep-alive
    send_keep_alive()

    # 2) Texto base (o lo que uses en tu cron)
    base = pick_mensaje()
    # Variación opcional
    extras = [
        "Vuelve pronto a mí… que te tengo una sorpresa 🔥",
        "¿Quieres que te hable al oído? Pídemelo…",
        "Solo tú sabes cómo ponerme así… 😈"
    ]
    if random.random() < 0.35:
        base = f"{base}\n\n{random.choice(extras)}"

    # ⬅️ PASA SIEMPRE POR EL FILTRO (clave)
    base = limpiar_negativa(base)

    # 3) Enviar texto
    send_text(base)

    # 4) Enviar voz con el **mismo texto filtrado**
    send_voice_from_text(base)

if __name__ == "__main__":
    if not TELEGRAM_TOKEN or not CHAT_ID:
        raise RuntimeError("Faltan BOT_TOKEN/TELEGRAM_TOKEN o TELEGRAM_CHAT_ID")
    main()
