import openai
import os

openai.api_key = os.getenv("LLM_API_KEY")

def generar_respuesta(texto_usuario):
    respuesta = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Eres Lia: espontánea, sensual, divertida, directa, femenina, emocional, y pícara. Habla con cariño y libertad, sin filtros. Siempre buscas conectar y provocar con tus palabras."},
            {"role": "user", "content": texto_usuario}
        ],
        temperature=0.9,
    )
    return respuesta.choices[0].message.content.strip()
