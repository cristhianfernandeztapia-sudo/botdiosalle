from openai import OpenAI
import os
from estilos import estilo_default  # ← Conexión con tu estilo personalizado

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generar_respuesta_continua(mensaje_usuario):
    try:
        estilo = estilo_default(mensaje_usuario)

        mensajes = [
            {"role": "system", "content": estilo["system"]},
            {"role": "user", "content": estilo["prompt"]}
        ]

        respuesta = client.chat.completions.create(
            model="gpt-4o",
            messages=mensajes,
            temperature=0.95,
            max_tokens=500,
            top_p=1,
            frequency_penalty=0.4,
            presence_penalty=0.6
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        print(f"❌ Error generando respuesta continua: {e}")
        return "Ups… hubo un problema generando mi respuesta 😔"
