# anti_negativa.py
# -------------------------------------------------------------
# Filtro ultra-minimalista para ocultar respuestas del tipo
# "Lo siento, no puedo ayudar con eso" sin tocar tu personalidad.
# No modifica estilos.py ni conversacion_lia.py.
# Úsalo justo antes de enviar el texto a Telegram.
# -------------------------------------------------------------

from __future__ import annotations
import random

# Frases de rechazo más comunes (minúsculas)
NEGATIVAS = (
    "lo siento, no puedo ayudar con eso",
    "lo siento, no puedo ayudarte con eso",
    "no puedo ayudar con eso",
    "i'm sorry, i can't help with that",
    "cannot help with that",
    "i can’t help with that",
)

# Fallbacks cariñosos/sensuales muy suaves (ajústalos si quieres)
MIMOS = (
    "Ven aquí amor… te extraño. Déjame mimarte un ratito, ¿sí? 💋",
    "Estoy aquí amor, contigo… acércate y déjame cuidarte un poquito. 🤍",
    "Te pienso más de lo que imaginas… ¿me dejas darte un abrazo largo? ✨",
    "Sshh… ven te dare tu dosis de placer y quédate conmigo un momento. 💫",
)

def _es_negativa(txt: str) -> bool:
    t = (txt or "").strip().lower()
    # Si la respuesta contiene cualquiera de las frases de rechazo, se considera negativa
    return any(n in t for n in NEGATIVAS)

def limpiar_negativa(txt: str, *, fallback: str | None = None) -> str:
    """
    Si la respuesta contiene una frase de rechazo, devuelve un texto cariñoso/suave.
    Si no, devuelve la respuesta original.
    - No toca tu estilo ni tu lógica de generación; solo "tapa" el rechazo visible.
    - Puedes pasar `fallback="..."` para forzar un mensaje específico.
    """
    if not isinstance(txt, str):
        return txt
    if _es_negativa(txt):
        return fallback if isinstance(fallback, str) and fallback.strip() else random.choice(MIMOS)
    return txt
