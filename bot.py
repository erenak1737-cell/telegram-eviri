import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
translator = GoogleTranslator(source="auto", target="tr")


def translate(text: str) -> str:
    try:
        return translator.translate(text)
    except Exception as e:
        return f"[Çeviri hatası: {e}]"


async def tr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = message.from_user

    # /tr komutunu gruptan sil (temiz kalsın)
    try:
        await message.delete()
    except Exception:
        pass

    if not message.reply_to_message:
        await context.bot.send_message(
            chat_id=user.id,
            text="Bir mesajı yanıtlarken /tr yaz."
        )
        return

    original = message.reply_to_message.text or message.reply_to_message.caption
    if not original:
        await context.bot.send_message(chat_id=user.id, text="Çevrilecek metin bulunamadı.")
        return

    result = translate(original)

    try:
        lang = detect(original)
        flag = "🇬🇧" if lang == "en" else "🌐"
    except LangDetectException:
        flag = "🌐"

    sender = message.reply_to_message.from_user
    sender_name = sender.first_name if sender else "Bilinmeyen"

    await context.bot.send_message(
        chat_id=user.id,
        text=f"{flag} **{sender_name}:**\n{original}\n\n🇹🇷 **Çeviri:**\n{result}",
        parse_mode="Markdown"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Merhaba! Herhangi bir mesajı yanıtlayıp /tr yaz — çevirisini sana özel gönderirim."
    )


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tr", tr))
    app.run_polling()
