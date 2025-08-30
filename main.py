import os
import openai
from estilos import PERSONALIDAD_LIA, obtener_tono

openai.api_key = os.getenv("OPENAI_API_KEY")

def generar_respuesta(mensaje_usuario):
    sistema = PERSONALIDAD_LIA
    tono = obtener_tono("sensual")  # Cambia esto por otro tono si deseas

    respuesta = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": sistema},
            {"role": "user", "content": mensaje_usuario}
        ],
        temperature=tono["temperatura"],
        frequency_penalty=tono["frecuencia"],
        presence_penalty=tono["presencia"]
    )
    return respuesta.choices[0].message.content.strip()

# Ejemplo de uso
if __name__ == "__main__":
    mensaje = "Hola Lia, ¿cómo estás?"
    print(generar_respuesta(mensaje))
