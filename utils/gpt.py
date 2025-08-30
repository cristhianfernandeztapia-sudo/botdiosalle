import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generar_respuesta(mensaje, sistema):
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": sistema},
                {"role": "user", "content": mensaje}
            ]
        )
        return respuesta.choices[0].message.content.strip()
    except Exception as e:
        return f"[Error al generar respuesta: {e}]"
