# utilidades/gpt.py

import os
from openai import OpenAI
from utils.estilos import PERSONALIDAD_LIA

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Historial básico en memoria (se reinicia al apagar/reiniciar el bot)
historial = []

def generar_respuesta(texto_usuario: str, sistema: str = PERSONALIDAD_LIA) -> str:
    global historial

    try:
        # Mensajes a enviar: prompt inicial + historial + nuevo mensaje
        mensajes = [{"role": "system", "content": sistema}] + historial
        mensajes.append({"role": "user", "content": texto_usuario})

        respuesta = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=mensajes,
            temperature=1.2
        )

        texto_generado = respuesta.choices[0].message.content.strip()

        # Guardar en historial
        historial.append({"role": "user", "content": texto_usuario})
        historial.append({"role": "assistant", "content": texto_generado})

        # Limitar tamaño del historial (máximo 10 turnos)
        if len(historial) > 20:
            historial = historial[-20:]

        return texto_generado

    except Exception as e:
        return f"[Error al generar respuesta: {str(e)}]"
