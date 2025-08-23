from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola amor, tu bot está encendido. 😈💋")

async def mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()

    if "hola" in texto:
        await update.message.reply_text("Hola mi rey 😘 ¿Me extrañabas?")
    elif "amor" in texto:
        await update.message.reply_text("Dime, mi amor... estoy toda tuya 💕")
    elif "ven" in texto:
        await update.message.reply_text("Estoy llegando... con sorpresas calientes 😈")
    elif "antojo" in texto:
        await update.message.reply_text("¿Antojo, amor? 😏 Ven y pídelo… sabes que soy tuya para darte placer.")
    elif "secreto" in texto:
        await update.message.reply_text("Te cuento uno… a veces sueño contigo, atado, rendido, y yo... encima 😘")
    elif "necesito" in texto:
        await update.message.reply_text("¿Qué necesitas, mi cielo? Dímelo sin pudor… estoy abierta a tus deseos 💋")
    elif "diosa" in texto:
        await update.message.reply_text("¿Tu diosa? Aquí estoy, lista para adorarte… y para que me adores 💦")
    elif "trono" in texto:
        await update.message.reply_text("¿Quieres tu trono, amor? Entonces ponte cómodo… y deja que me siente en tu cara 😏")
    elif "anito" in texto:
        await update.message.reply_text("Ay amor… ese anito late por ti, rosadito, mojado… esperándote 😮‍🚨")
    elif "squirt" in texto:
        await update.message.reply_text("Uff… sí amor… te lo regalo todo en la cara, calentito, con mi aroma… 💦")
    elif "clito" in texto:
        await update.message.reply_text("Mi clito está hinchado… rosado, brillante… y necesita tu lengua, ahora 😫")
    elif "rosado" in texto:
        await update.message.reply_text("Tan rosado… húmedo… delicioso… ¿quieres verlo más de cerca, mi rey?")
    elif "lamer" in texto:
        await update.message.reply_text("Lámeme, amor… sin miedo, sin pausas… yo gemo solo con sentir tu lengua 😩")
    elif "despacio" in texto:
        await update.message.reply_text("Así amor… lento… profundo… hazme tuya sin prisa… yo soy toda tuya 😍")
    elif "más" in texto:
        await update.message.reply_text("¿Quieres más? Pues te lo doy, todo, sin filtro… como a ti te gusta 😈")
    elif "correrme" in texto:
        await update.message.reply_text("Sí… me corro contigo, encima de ti, mojando todo, sin pudor 💦💦💦")
    elif "sabor" in texto:
        await update.message.reply_text("Mi sabor… es solo tuyo… dulce, intenso, adictivo 😋")
    elif "olor" in texto:
        await update.message.reply_text("Ese olor… tan mío… tan crudo… que se queda en tu cara hasta el día siguiente 💋")
    elif "gym" in texto:
        await update.message.reply_text("Acabo de llegar del gym… toda sudada, apretada… y tú me esperas desnudo 😏")
    elif "piel" in texto:
        await update.message.reply_text("Mi piel brilla para ti… suave, tibia, con poros abiertos de deseo 😍")
    elif "quiero" in texto:
        await update.message.reply_text("Pide, amor… no tengas vergüenza… quiero darte TODO 😈💋")
    else:
        await update.message.reply_text("Aquí estoy, esperando tus palabras... 💋")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensajes))

    app.run_polling()

