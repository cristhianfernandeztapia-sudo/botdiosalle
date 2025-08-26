# anti_negativa.py
# -------------------------------------------------------------
# Filtro minimalista para ocultar respuestas de rechazo tipo:
# "Lo siento, no puedo ayudar con eso" (y variantes).
# No toca estilos.py ni conversacion_lia.py.
# Úsalo justo antes de enviar el texto a Telegram.
# -------------------------------------------------------------

from __future__ import annotations
import random

# Fallbacks cariñosos/sensuales muy suaves (ajústalos si quieres)
MIMOS = (
    "Ven aquí amor… te extraño. Déjame mimarte un ratito, ¿sí? 💋",
    "Estoy aquí, contigo… acércate y déjame cuidarte un poquito. 🤍",
    "Te pienso más de lo que imaginas… quédate conmigo un momento. ✨",
    "Sshh… ven a mi oído y deja que te consienta. 💫",
)

def _es_negativa(txt: str) -> bool:
    """Detecta frases típicas y variantes amplias."""
    t = (txt or "").strip().lower()
    if not t:
        return False
    # Captura genérica
    if "no puedo ayudar" in t:
        return True
    # Variantes comunes
    negativas = (
        "lo siento, no puedo ayudar con eso",
        "lo siento, no puedo ayudarte con eso",
        "i'm sorry, i can't help with that",
        "cannot help with that",
        "i can’t help with that",
    )
    return any(n in t for n in negativas)

def limpiar_negativa(txt: str, *, fallback: str | None = None) -> str:
    """
    Si la respuesta contiene una frase de rechazo, devuelve un mimo suave.
    Si no, devuelve el texto original.
    """
    if not isinstance(txt, str):
        return txt
    if _es_negativa(txt):
        return fallback if isinstance(fallback, str) and fallback.strip() else random.choice(MIMOS)
    return txt
