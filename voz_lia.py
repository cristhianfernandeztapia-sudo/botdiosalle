import requests, os
ELEVEN_API_KEY = os.getenv('ELEVEN_API_KEY')
VOICE_ID = "XB0fDUnXU5powFXDhCwa"
def generar_audio(texto: str):
 url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
 headers = {"xi-api-key": ELEVEN_API_KEY, "Content-Type": "application/json"}
 body = {"text": texto, "model_id": "eleven_monolingual_v1", "voice_settings": {"stability": 0.40, "similarity_boost": 0.85, "style": 0.75, "use_speaker_boost": True}}
 r = requests.post(url, json=body, headers=headers)
 with open("voz_lia.mp3", "wb") as f:
  f.write(r.content)
