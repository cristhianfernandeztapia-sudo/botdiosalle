# conversacion_lia.py

import random
import openai
from estilos import estilo_lia

frases_de_transicion = [
    "¿Quieres que te cuente algo más, amor?",
    "Estoy aquí… ¿seguimos hablando?",
    "¿Te gustaría que siga con esto?",
    "Si quieres, puedo seguir contándote todo 💋",
    "Dímelo tú… ¿quieres más?",
    "Estoy encendida… y tú también 😈",
]

historial = []

def generar_respuesta_continua(texto_usuario):
    historial.append({"role": "user", "content": texto_usuario})

    mensajes = [{"role": "system", "content": estilo_lia}] + historial

    respuesta = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=mensajes,
        temperature=1.1,
        max_tokens=600,
    )

    contenido = respuesta.choices[0].message.content.strip()
    contenido += "\n\n" + random.choice(frases_de_transicion)

    historial.append({"role": "assistant", "content": contenido})
    return contenido
