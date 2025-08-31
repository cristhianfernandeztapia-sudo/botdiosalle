# utilidades/gpt.py

import os
from openai import OpenAI
from utils.estilos import PERSONALIDAD_LIA  # Solo importa lo que necesitas (o puedes traer más si usas el resto)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generar_respuesta(texto_usuario: str, sistema: str = PERSONALIDAD_LIA) -> str:
    try:
        respuesta = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": sistema},
                {"role": "user", "content": texto_usuario}
            ],
            temperature=1.4  # 🔥 Creatividad e improvisación sensual activada
        )
        return respuesta.choices[0].message.content.strip()
    except Exception as e:
        return f"[Error al generar respuesta: {str(e)}]"
