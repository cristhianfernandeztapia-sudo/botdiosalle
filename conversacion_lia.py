from openai import OpenAI
import os, time, traceback
from estilos import estilo_default

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generar_respuesta_continua(mensaje_usuario: str) -> str:
    try:
        # 1) Fallback si el mensaje es muy corto (evita respuestas vacías / bloqueos)
        if not mensaje_usuario or len(mensaje_usuario.strip()) < 3:
            mensaje_usuario = "Hola Lia, respóndeme caliente y cariñosa, improvisa."

        estilo = estilo_default(mensaje_usuario)
        mensajes = [
            {"role": "system", "content": estilo["system"]},
            {"role": "user", "content": estilo["user"]}
        ]

        # 2) Reintentos con backoff (por si Render está “frío” o hay timeouts)
        intentos = 3
        for i in range(intentos):
            try:
                resp = client.chat.completions.create(
                    model="gpt-4o",
                    messages=mensajes,
                    temperature=0.95,
                    max_tokens=600,   # un poco más de margen
                    top_p=1,
                    frequency_penalty=0.4,
                    presence_penalty=0.6,
                )
                texto = (resp.choices[0].message.content or "").strip()
                if texto:
                    # 3) Sanitizar mínimos (evita None y espacios)
                    return texto
                else:
                    raise ValueError("Respuesta vacía del modelo")
            except Exception as inner:
                # log breve por intento
                print(f"⚠️ Intento {i+1}/{intentos} falló: {inner}")
                if i < intentos - 1:
                    time.sleep(1.5 * (i + 1))  # backoff progresivo
                else:
                    raise  # sale al except externo

    except Exception as e:
        # 4) Log detallado en Render para ver el error real
        print("❌ Error generando respuesta continua:")
        print(traceback.format_exc())
        return "Ups… tuve un pequeño problema, amor. Dímelo de nuevo y te respondo rico 😘"
