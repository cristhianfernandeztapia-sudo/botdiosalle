from gtts import gTTS
import os

def generar_audio(texto, nombre_archivo="voz_lia.mp3"):
    try:
        tts = gTTS(text=texto, lang='es')
        tts.save(nombre_archivo)
        return nombre_archivo
    except Exception as e:
        print(f"Error generando voz: {e}")
        return None