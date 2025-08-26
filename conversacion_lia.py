# conversacion_lia.py
from openai import OpenAI
import os, time, traceback, re

# ✅ Usamos tu función real del estilo
from estilos import estilo_predeterminado as estilo_default

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DEBUG = os.getenv("DEBUG_LIA", "false").lower() in ("1", "true", "yes")

# Palabras que activan modo narrativo
NARRATIVE_TRIGGERS = (
    "relato", "historia", "cuéntame", "cuentame",
    "narra", "narración", "narracion", "cuento",
    "cuadro", "escena"
)

def _es_narrativo(txt: str) -> bool:
    if not isinstance(txt, str):
        return False
    t = txt.lower()
    return any(k in t for k in NARRATIVE_TRIGGERS)

def generar_respuesta_continua(mensaje_usuario: str) -> str:
    try:
        # 1) Fallback si el mensaje es muy corto
        if not mensaje_usuario or len(mensaje_usuario.strip()) < 3:
            mensaje_usuario = "Hola Lia, improvisa con cariño y fluidez."

        # 2) Construir estilo/persona desde tu estilos.py
        estilo = estilo_default(mensaje_usuario)

        # 3) Detectar si pide relato / historia y ajustar mensajes
        es_narrativo = _es_narrativo(mensaje_usuario)

        # Mensaje de sistema / usuario según tus claves
        system_msg = estilo["sistema"]
        user_msg   = estilo["usuario"]

        # 🔸 Modo narrativo: añadimos guía neutra de narrativa (sin cambiar personalidad)
        if es_narrativo:
            user_msg = (
                f"{user_msg}\n\n"
                "[MODO_NARRATIVO]\n"
                "- Escribe como relato en 1–3 escenas con ritmo (inicio → desarrollo → cierre).\n"
                "- Detalles sensoriales y continuidad temporal; evita repetición de frases.\n"
                "- Cohesiona con transiciones suaves; evita listas; usa párrafos fluidos.\n"
                "- Mantén la voz del personaje estable.\n"
                "- Extensión objetivo: 400–900 palabras."
            )

        mensajes = [
            {"role": "system", "content": system_msg},
            {"role": "user",    "content": user_msg}
        ]

        # 4) Parámetros base y modo narrativo
        temperature       = 0.95
        presence_penalty  = 0.60
        frequency_penalty = 0.40
        max_tokens        = 600

        if es_narrativo:
            temperature       = 1.05   # un poco más de variación
            presence_penalty  = 0.80   # explora más ideas/recursos
            frequency_penalty = 0.30   # permite reforzar ideas sin sonar repetitivo
            max_tokens        = 1200   # relatos largos

        if DEBUG:
            print(f"[LIA DEBUG] narrativo={es_narrativo} temp={temperature} "
                  f"presence={presence_penalty} freq={frequency_penalty} max={max_tokens}")

        # 5) Reintentos con backoff
        intentos = 3
        for i in range(intentos):
            try:
                resp = client.chat.completions.create(
                    model="gpt-4o",
                    messages=mensajes,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=1,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                )
                texto = (resp.choices[0].message.content or "").strip()
                if texto:
                    return texto
                else:
                    raise ValueError("Respuesta vacía del modelo")
            except Exception as inner:
                if DEBUG:
                    print(f"[LIA DEBUG] intento {i+1}/{intentos} falló: {inner}")
                if i < intentos - 1:
                    time.sleep(1.5 * (i + 1))  # backoff progresivo
                else:
                    raise

    except Exception:
        print("❌ Error generando respuesta continua:")
        print(traceback.format_exc())
        return "Ups… tuve un pequeño problema, amor. Dímelo de nuevo y te respondo con calma y cariño 😘"
