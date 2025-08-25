from gtts import gTTS
import os

def generar_audio_lia(texto, nombre_archivo="respuesta_lia.mp3"):
    try:
        tts = gTTS(text=texto, lang="es")
        tts.save(nombre_archivo)
        return nombre_archivo
    except Exception as e:
        print(f"Error generando audio: {e}")
        return None
