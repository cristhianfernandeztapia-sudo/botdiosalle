import openai
import os

def generar_respuesta_continua(inmediato):
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres Lia: espontánea, sensual, divertida, directa, femenina, emocional, y pícara. Habla con cariño y libertad, sin filtros. Siempre buscas conectar y provocar con tus palabras."},
                {"role": "user", "content": inmediato}
            ],
            temperature=0.95,
            max_tokens=500,
            top_p=1,
            frequency_penalty=0.4,
            presence_penalty=0.6
        )
        return respuesta.choices[0].message["content"]
    except Exception as e:
        print(f"❌ Error generando respuesta continua: {e}")
        return "Ups… hubo un problema generando mi respuesta 😔"
