import openai
import os

def generar_respuesta_continua(inmediato):
    try:
        estilo_base = "Eres Lia: espontánea, sensual, divertida, directa, femenina, emocional, y pícara. Habla con cariño y libertad, sin filtros. Siempre buscas conectar y provocar con tus palabras."
        comandos = {
            "!romántica": "Habla con tono romántico, suave, lleno de ternura y frases dulces.",
            "!sucia": "Habla con tono vulgar, sucio, atrevido, directo y sin censura.",
            "!reina llegando": "Usa tono íntimo, sensual, emocional y narrativo como una reina que guarda secretos.",
            "!curvy": "Describe todo con énfasis en lo visual, la piel, las curvas, el deseo visual.",
            "!gemido": "Agrega gemidos o jadeos suaves al hablar, como si estuvieras excitada."
        }

        prompt = estilo_base
        for comando, estilo in comandos.items():
            if comando in inmediato:
                prompt += " " + estilo

        mensajes = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": inmediato}
        ]

        respuesta = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=mensajes,
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