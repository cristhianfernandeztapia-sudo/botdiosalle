# anti_negativa.py
# -------------------------------------------------------------
# Limpia cualquier negativa del modelo (ES/EN), elimina líneas
# completas con negativas y remueve "sobras" como "ayudar con eso".
# Devuelve el primer bloque sano; si no hay, responde con un mimo.
# -------------------------------------------------------------

from __future__ import annotations
import re
import random

# Patrones amplios de NEGATIVAS (disparan eliminación de la línea)
NEGATIVAS_PATTERNS = [
    r"\blo siento\b",
    r"\bperd[oó]n\b",
    r"\bno puedo\b",
    r"\bno (?:te )?puedo ayudar\b",
    r"\bno puedo (?:asistir|hacer|cumplir)\b",
    r"\bno est[áa] (?:permitido|autorizad[oa])\b",
    r"\bno es apropiado\b",
    r"\bcomo modelo de lenguaje\b",
    # EN
    r"\bi'?m sorry\b",
    r"\bcan'?t help\b",
    r"\bcannot help\b",
    r"\bn(?:ot )?allowed\b",
    r"\bpolicy\b",
]

# "Sobras" típicas cuando se borran fragmentos (limpieza adicional)
LEFTOVER_PATTERNS = [
    r"\bayudar(?:te)? con eso\b",
    r"\basistir con esa petici[oó]n\b",
    r"\bhacer eso\b",
    r"\bcon esa petici[oó]n\b",
    r"\bayudar(?:te)? en eso\b",
]

MIMOS = (
    "Ven aquí amor… te extraño. Déjame mimarte un ratito, ¿sí? 💋",
    "Estoy aquí contigo… acércate y déjame cuidarte un poquito. 🤍",
    "Te pienso más de lo que imaginas… quédate conmigo un momento. ✨",
    "Sshh… ven a mi oído y deja que te consienta. 💫",
)

def _match_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text, flags=re.IGNORECASE) for p in patterns)

def _strip_patterns(text: str, patterns: list[str]) -> str:
    out = text
    for p in patterns:
        out = re.sub(p, "", out, flags=re.IGNORECASE)
    # compactar espacios / signos sueltos
    out = re.sub(r"\s{2,}", " ", out)
    out = re.sub(r"\s*([,.;:!?])", r"\1", out)
    out = out.strip(" ,.;:!?\n\t").strip()
    return out

def limpiar_negativa(txt: str, *, fallback: str | None = None) -> str:
    """
    - Si un bloque contiene negativas → elimina la línea completa.
    - Si después quedan "sobras" → las borra.
    - Devuelve el primer bloque sano; si no hay, retorna un mimo.
    """
    if not isinstance(txt, str):
        return txt or ""

    # Partir por párrafos/líneas
    bloques = [b.strip() for b in re.split(r"\r?\n+", txt) if b and b.strip()]
    candidatos: list[str] = []

    for b in bloques:
        if _match_any(b, NEGATIVAS_PATTERNS):
            # Intento de limpieza; si queda muy corto, descartar
            limpio = _strip_patterns(b, NEGATIVAS_PATTERNS + LEFTOVER_PATTERNS)
            if limpio and len(limpio.split()) >= 6:
                candidatos.append(limpio)
            # si no, descartamos el bloque entero (era negativa pura)
        else:
            # Limpieza suave por si el modelo dejó restos mínimos
            limpio = _strip_patterns(b, LEFTOVER_PATTERNS)
            if limpio:
                candidatos.append(limpio)

    resultado = (candidatos[0] if candidatos else "").strip()
    if resultado:
        return resultado

    # Si no quedó nada sano:
    return fallback if (isinstance(fallback, str) and fallback.strip()) else random.choice(MIMOS)
