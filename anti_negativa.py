# anti_negativa.py
# -------------------------------------------------------------
# Filtra y limpia cualquier negativa del modelo (en español/inglés)
# y devuelve un texto suave si todo el contenido es negativo.
# También elimina párrafos/lineas que contengan negativas y
# deja solo el primer bloque “sano”.
# -------------------------------------------------------------

from __future__ import annotations
import re
import random

# Frases que jamás queremos que salgan
NEGATIVAS_PATTERNS = [
    r"\blo siento\b",
    r"\bno puedo\b",
    r"\bno podr[ée]?\b",
    r"\bno (?:te )?puedo ayudar\b",
    r"\bno estoy (?:autorizad[ao]|habilitad[ao])\b",
    r"\bcomo modelo de lenguaje\b",
    r"\bno est[áa] permitido\b",
    r"\bi'?m sorry\b",
    r"\bcan'?t help with that\b",
    r"\bcannot help\b",
]

# Mimos por si hay que sustituir por completo
MIMOS = (
    "Ven aquí amor… te extraño. Déjame mimarte un ratito, ¿sí? 💋",
    "Estoy aquí contigo… acércate y déjame cuidarte un poquito. 🤍",
    "Te pienso más de lo que imaginas… quédate conmigo un momento. ✨",
    "Sshh… ven a mi oído y deja que te consienta. 💫",
)

def _contiene_negativa(t: str) -> bool:
    t = (t or "").strip()
    if not t:
        return False
    tl = t.lower()
    if "no puedo ayudar" in tl:
        return True
    return any(re.search(p, t, flags=re.IGNORECASE) for p in NEGATIVAS_PATTERNS)

def _limpiar_linea(t: str) -> str:
    """Elimina las frases negativas dentro de una línea conservando el resto."""
    if not t:
        return t
    limpio = t
    for p in NEGATIVAS_PATTERNS:
        limpio = re.sub(p, "", limpio, flags=re.IGNORECASE)
    # Quitar restos como dobles espacios/puntuación sobrante
    limpio = re.sub(r"\s{2,}", " ", limpio).strip(" ,.;:!?\n\t").strip()
    return limpio

def limpiar_negativa(txt: str, *, fallback: str | None = None) -> str:
    """
    - Quita líneas/párrafos que sean puramente negativos.
    - Limpia frases negativas incrustadas.
    - Devuelve el PRIMER bloque sano.
    - Si TODO era negativo, devuelve un mimo suave.
    """
    if not isinstance(txt, str):
        return txt or ""

    # Particionamos por líneas/párrafos
    bloques = [b.strip() for b in re.split(r"\n{1,}|\r{1,}", txt) if b and b.strip()]
    bloques_limpios = []

    for b in bloques:
        if _contiene_negativa(b):
            # Intentar limpiar frases negativas internas
            b2 = _limpiar_linea(b)
            if b2 and not _contiene_negativa(b2):
                bloques_limpios.append(b2)
            # Si sigue siendo negativa, la descartamos
        else:
            bloques_limpios.append(b)

    resultado = (bloques_limpios[0] if bloques_limpios else "").strip()

    if resultado:
        return resultado

    # Si no hay nada sano, devolvemos mimo
    return (fallback if (isinstance(fallback, str) and fallback.strip()) else random.choice(MIMOS))
