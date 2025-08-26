# conversacion_lia.py
from openai import OpenAI
import os, time, traceback, re

# ── Importa tu estilo (system/user) y cae a un fallback si no existe ──
try:
    from estilos import estilo_default as estilo_base
except Exception:
    estilo_base = None

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DEBUG = os.getenv("DEBUG_LIA", "false").lower() in ("1", "true", "yes")

# Disparadores del modo narrativo
NARRATIVE_TRIGGERS = (
    "relato", "historia", "cuéntame", "cuentame",
    "narra", "narración", "narracion", "cuento", "escena"
)

# Detección de negativas del modelo (por si llegaran)
NEGATIVE_PATTERNS = (
    r"\blo siento\b",
    r"\bno puedo\b",
    r"\bno (?:te )?puedo ayudar\b",
    r"\bno est[áa] permitido\b",
    r"i'?m sorry",
    r"can'?t help",
    r"cannot help",
)

def _is_narrative(text: str) -> bool:
    return isinstance(text, str) and any(k in text.lower() for k in NARRATIVE_TRIGGERS)

def _normalize_estilo(mensaje: str) -> tuple[str, str]:
    """
    Normaliza el estilo a (system, user). Si no hay estilos, usa un fallback suave.
    """
    if callable(estilo_base):
        est = estilo_base(mensaje)
    else:
        est = {"system": "Te llamas Lia. Responde con cariño y fluidez.", "user": mensaje}

    system = est.get("system") or est.get("sistema") or ""
    user   = est.get("user")   or est.get("usuario") or mensaje
    return system, user

def _seems_negative(t: str) -> bool:
    if not isinstance(t, str):
        return False
    return any(re.search(p, t, flags=re.IGNORECASE) for p in NEGATIVE_PATTERNS)

def generar_respuesta_continua(mensaje_usuario: str) -> str:
    try:
        if not mensaje_usuario or len(mensaje_usuario.strip()) < 2:
            mensaje_usuario = "Hola Lia, improvisa con cariño y fluidez."

        system, user = _normalize_estilo(mensaje_usuario)
        es_narrativo = _is_narrative(mensaje_usuario)

        # Modo narrativo: guía de estructura/variedad (no toca tu personalidad)
        if es_narrativo:
            user += (
                "\n\n[MODO_NARRATIVO]\n"
                "- Escribe como historia continua (inicio → desarrollo → cierre).\n"
                "- Detalles sensoriales y transiciones suaves; evita frases de rechazo.\n"
                "- 400–900 palabras; párrafos fluidos, no listas."
            )
            temperature, presence, freq, max_toks = 1.05, 0.80, 0.30, 1200
        else:
            temperature, presence, freq, max_toks = 0.95, 0.60, 0.40, 600

        mensajes = [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ]

        # Reintentos con backoff
        for i in range(3):
            try:
                resp = client.chat.completions.create(
                    model="gpt-4o",
                    messages=mensajes,
                    temperature=temperature,
                    max_tokens=max_toks,
                    top_p=1,
                    frequency_penalty=freq,
                    presence_penalty=presence,
                )
                texto = (resp.choices[0].message.content or "").strip()
                if texto:
                    # Si el modelo aún intentara una negativa, amortiguamos aquí;
                    # luego main.py + anti_negativa rematan el filtrado.
                    if _seems_negative(texto):
                        return "Ven aquí… quiero contarte algo bonito, ¿me dejas? 🤍"
                    return texto
                else:
                    raise ValueError("Respuesta vacía del modelo")
            except Exception as inner:
                if DEBUG:
                    print(f"[LIA DEBUG] intento {i+1}/3 falló: {inner}")
                if i < 2:
                    time.sleep(1.5 * (i + 1))

        raise RuntimeError("Sin respuesta útil del modelo")

    except Exception:
        print("❌ Error generando respuesta continua:")
        print(traceback.format_exc())
        return "Ups… tuve un pequeño problema, amor. Dímelo de nuevo y te respondo con calma y cariño 😘"
