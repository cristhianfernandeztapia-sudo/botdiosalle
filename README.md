# Diosa Lia Bot 🔥

Bot sensual con voz y respuestas personalizadas en Telegram, usando FastAPI + OpenAI.

## Archivos principales
- `main.py` – servidor FastAPI con webhook de Telegram
- `estilos.py` – define el estilo de respuesta de Lia
- `voz_lia.py` – genera audio con voz
- `conversacion_lia.py` – genera texto con estilo Lia

## Instrucciones básicas
1. Crea `.env` con tus claves:
   ```env
   BOT_TOKEN=tu_token_de_telegram
   OPENAI_API_KEY=tu_api_key_openai
   ```
2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta:
   ```bash
   uvicorn main:app --reload
   ```