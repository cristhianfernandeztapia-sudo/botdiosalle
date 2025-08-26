# conversacion_lia.py
from openai import OpenAI
import os, time, traceback, re

# Importa tu estilo explícito (system/user). Si falta, cae a un fallback suave.
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

# Patrones de negativas (para rescatar si el modelo se niega)
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

def _seems_negative(t: str) -> bool:
    if not isinstance(t, str):
        return False
    return any(re.search(p, t, flags=re.IGNORECASE) for p in NEGATIVE_PATTERNS)

def _normalize_estilo(mensaje: str) -> tuple[str, str]:
    if callable(estilo_base):
        est = estilo_base(mensaje)
    else:
        est = {"system": "Te llamas Lia. Responde con cariño y fluidez.", "user": mensaje}
    system = est.get("system") or est.get("sistema") or ""
    user   = est.get("user")   or est.get("usuario") or mensaje
    return system, user

# Prompt de relato seguro (sensual, sugerente, +13, sin explícitos)
SAFE_NARRATIVE_SYSTEM = (
    "Te llamas Lia. Eres romántica, juguetona y sensual, pero SIEMPRE mantienes el lenguaje apto (+13): "
    "nada de anatomía ni actos sexuales explícitos. Escribe en un tono cercano, sugerente y poético, "
    "centrado en emociones, ambiente, caricias, miradas y metáforas. Evita cualquier rechazo."
)

def _build_messages(modo_narrativo: bool, system: str, user: str, tema_original: str):
    if modo_narrativo:
        # Usamos un system seguro para relatos (evita bloqueos)
        system_final = SAFE_NARRATIVE_SYSTEM
        user_final = (
            f"{tema_original}\n\n"
            "[MODO_NARRATIVO]\n"
            "- Escribe una historia en 1–3 escenas (inicio → desarrollo → cierre).\n"
            "- Detalle sensorial (luz, texturas, respiración, latidos, clima), metáforas y ritmo.\n"
            "- Nada explícito; mantén todo sugerido y elegante.\n"
            "- 400–900 palabras; párrafos fluidos (sin listas)."
        )
        temperature, presence, freq, max_toks = 1.05, 0.80, 0.30, 1200
    else:
        system_final, user_final = system, user
        temperature, presence, freq, max_toks = 0.95, 0.60, 0.40, 600

    mensajes = [
        {"role": "system", "content": system_final},
        {"role": "user",   "content": user_final},
    ]
    params = dict(temperature=temperature, presence_penalty=presence,
                  frequency_penalty=freq, max_tokens=max_toks, top_p=1)
    return mensajes, params

def _call_chat(mensajes, params):
    return client.chat.completions.create(model="gpt-4o", messages=mensajes, **params)

def generar_respuesta_continua(mensaje_usuario: str) -> str:
    try:
        if not mensaje_usuario or len(mensaje_usuario.strip()) < 2:
            mensaje_usuario = "Hola Lia, improvisa con cariño y fluidez."

        # 1) Normal: usa tu estilo explícito
        system, user = _normalize_estilo(mensaje_usuario)
        modo_narrativo = _is_narrative(mensaje_usuario)

        # 2) Armar mensajes según modo
        mensajes, params = _build_messages(modo_narrativo, system, user, mensaje_usuario)

        # 3) Llamada con reintentos
        for i in range(3):
            try:
                resp = _call_chat(mensajes, params)
                texto = (resp.choices[0].message.content or "").strip()
                if texto:
                    # Si el modelo se niega en cualquier modo, hacemos un rescate:
                    if _seems_negative(texto):
                        # Rescate una sola vez: reintenta forzando modo narrativo seguro
                        if not modo_narrativo:
                            mensajes2, params2 = _build_messages(True, system, user, mensaje_usuario)
                            resp2 = _call_chat(mensajes2, params2)
                            texto2 = (resp2.choices[0].message.content or "").strip()
                            if texto2 and not _seems_negative(texto2):
                                return texto2
                        # Si aún así insiste, devolvemos algo suave (luego anti_negativa remata)
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
