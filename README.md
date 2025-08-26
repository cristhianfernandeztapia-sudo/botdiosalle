# BotLia (FastAPI + Telegram + OpenAI + ElevenLabs)

Servicio Web (webhook) + Cron para mensajes proactivos. Opción de voz con **Carlota** (ElevenLabs). Listo para Render con Blueprint (`render.yaml`).

---

## Contenido

```
botlia/
├─ README.md
├─ .env.example
├─ requirements.txt
├─ render.yaml
├─ estilos.py
├─ main.py
├─ cron_lia.py
├─ voz_lia.py
└─ utils/
   ├─ gpt.py
   ├─ telegram.py
   └─ logger.py
```

---

## Variables (Render → Environment)

### Web Service (botlia)
- `BOT_TOKEN` **(obligatoria)**
- `BASE_URL` **(obligatoria)** — ej. `https://tuapp.onrender.com`
- `WEBHOOK_SECRET` **(obligatoria)**
- `OPENAI_API_KEY` *(opcional)*
- `OPENAI_MODEL` *(opcional, por defecto `gpt-4o-mini`)*
- `SEND_AUDIO` *(true/false)*
- `ELEVEN_API_KEY` *(si usas voz)*
- `ELEVEN_VOICE_ID` *(opcional, Carlota por defecto `XB0fDUnXU5powFXDhCwa`)*
- `ELEVEN_MODEL_ID` *(opcional, por defecto `eleven_multilingual_v2`)*

### Cron (lia-cron)
- `BOT_TOKEN` **(obligatoria)**
- `TELEGRAM_USER_ID` **(obligatoria)**
- `OPENAI_API_KEY` *(opcional)*
- `OPENAI_MODEL` *(opcional, por defecto `gpt-4o-mini`)*
- `CRON_SEND_AUDIO` *(true/false)*
- `ELEVEN_API_KEY` / `ELEVEN_VOICE_ID` / `ELEVEN_MODEL_ID` *(si quieres voz en cron)*

> Puedes guiarte por `.env.example` para no olvidar nada.

---

## Deploy en Render (express)

1. Sube este proyecto a un repo (o usa **Upload files** en GitHub).
2. En Render: **New → Blueprint** y selecciona el repo (usa `render.yaml`).
3. Completa las variables de **ambos servicios** (Web y Cron).
4. Deploy del **Web**. El webhook se fija automáticamente si `BASE_URL` + `WEBHOOK_SECRET` están definidos.  
   También puedes ir a `GET /set_webhook` para fijarlo manualmente.
5. Escríbele **/start** a tu bot en Telegram.
6. Si `SEND_AUDIO=true`, te responde **texto + audio Carlota**.
7. Ejecuta el **Cron** manualmente o espera el schedule (cada 30 min).  
   Si `CRON_SEND_AUDIO=true`, también te llega audio.

---

## Personalización rápida

- Edita `estilos.py`: nombre/emoji, mensajes base del cron y el `PROMPT_PERSONA` (tono de GPT).
- Cambia la frecuencia del cron en `render.yaml` (`schedule`).

---

## Notas técnicas

- OpenAI usa el **cliente v1** de `openai` (evitamos el módulo legacy `openai.ChatCompletion.create` sin cliente).  
  Implementamos con `from openai import OpenAI`.
- ElevenLabs devuelve **MP3** y lo enviamos vía `sendAudio` (sin `ffmpeg`).
- Si no hay `OPENAI_API_KEY`, funciona igual con **textos base**.
- Si no hay `ELEVEN_API_KEY`, envía **solo texto** (no rompe).
- Validación de webhook con header `X-Telegram-Bot-Api-Secret-Token`.

---

## Desarrollo local (opcional)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # edita tus claves
uvicorn main:app --reload
```

---

## Endpoints

- `GET /health` → ok
- `GET /` → ok
- `GET /set_webhook` → fija el webhook (si tienes `BASE_URL` y `WEBHOOK_SECRET`)
- `POST /telegram/webhook` → endpoint de Telegram
```

