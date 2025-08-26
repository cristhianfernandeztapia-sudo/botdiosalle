# telegram_webhook.py
# Manejador "silencioso": procesa el update si lo necesitas para logs/estados,
# pero NO envía mensajes (para evitar duplicados y frases de rechazo).
# Si en el futuro quieres que esta ruta envíe algo, pásalo SIEMPRE por anti_negativa.limpiar_negativa.

import json
import traceback

def manejar_update(update: dict) -> None:
    """
    Procesa el update de Telegram sin emitir respuestas.
    Útil para métricas, logs, analíticas, etc.
    """
    try:
        # Log mínimo (evita volcar binarios grandes)
        msg = update.get("message", {})
        chat = msg.get("chat", {})
        text = msg.get("text", "")
        print(f"[webhook-silent] chat_id={chat.get('id')} text={text!r}")
        # Aquí podrías guardar métricas, estados, etc.
        return
    except Exception:
        print("[webhook-silent] error procesando update:")
        print(traceback.format_exc())
        return
