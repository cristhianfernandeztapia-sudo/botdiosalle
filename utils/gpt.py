# utilidades/gpt.py

import os
from openai import OpenAI
from utils.estilos import PERSONALIDAD_LIA
from memoria import cargar_memoria, guardar_memoria

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Límite de historial por usuario (por token/contexto)
MAX_HISTORIAL = 20

def generar_respuesta(texto_usuario: str, sistema: str = PERSONALIDAD_LIA, chat_id: str = "default") -> str:
    try:
        # Cargar historial desde memoria
        historial = cargar_memoria(chat_id).get("historial", [])

        # Armar mensaje para la API
        mensajes = [{"role": "system", "content": sistema}] + historial
        mensajes.append({"role": "user", "content": texto_usuario})

        # Llamar a OpenAI
        respuesta = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=mensajes,
            temperature=1.0
        )

        texto_generado = respuesta.choices[0].message.content.strip()

        # Actualizar historial
        historial.append({"role": "user", "content": texto_usuario})
        historial.append({"role": "assistant", "content": texto_generado})

        # Limitar historial a los últimos 20 mensajes
        if len(historial) > MAX_HISTORIAL:
            historial = historial[-MAX_HISTORIAL:]

        # Guardar en archivo
        guardar_memoria(chat_id, {"historial": historial})

        return texto_generado

    except Exception as e:
        return f"[Error al generar respuesta: {str(e)}]"
