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
        await update.message.reply_text("Dime, mi amor... estoy toda tuya 💞")
    elif "ven" in texto:
        await update.message.reply_text("Estoy llegando... con sorpresas calientes 😈")
    else:
        await update.message.reply_text("Aquí estoy, esperando tus palabras... 💋")

if __name__ == '__main__':
    import os
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensajes))

    print("Bot corriendo...")
    app.run_polling()
