from openai import OpenAI
import os, time, traceback

# Usa SIEMPRE tu estilo base sin tocarlo
from estilos import estilo_default

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DEBUG = os.getenv("DEBUG_LIA", "false").lower() in ("1", "true", "yes")

def generar_respuesta_continua(mensaje_usuario: str) -> str:
    try:
        prompt = (mensaje_usuario or "").strip()
        if len(prompt) < 2:
            prompt = "Hola Lia, improvisa con tu estilo."

        est = estilo_default(prompt)
        mensajes = [
            {"role": "system", "content": est.get("system") or est.get("sistema") or ""},
            {"role": "user",   "content": est.get("user")   or est.get("usuario") or prompt},
        ]

        for i in range(3):  # reintentos cortos por frío de Render
            try:
                r = client.chat.completions.create(
                    model="gpt-4o",
                    messages=mensajes,
                    temperature=1.00,   # tu estilo, sin frenos
                    max_tokens=1000,    # margen para textos largos
                    top_p=1,
                    frequency_penalty=0.3,
                    presence_penalty=0.6,
                )
                t = (r.choices[0].message.content or "").strip()
                if t:
                    return t
                else:
                    raise ValueError("Respuesta vacía")
            except Exception as e:
                if DEBUG: print(f"[LIA DEBUG] intento {i+1}/3: {e}")
                if i < 2:
                    time.sleep(1.2 * (i + 1))

        return "Amor, tuve un tropiezo técnico. Dímelo de nuevo y lo intento otra vez. 💗"
    except Exception:
        print("❌ Error generar_respuesta_continua:")
        print(traceback.format_exc())
        return "Amor, algo falló aquí. Dímelo otra vez y te respondo al tiro. 💗"
