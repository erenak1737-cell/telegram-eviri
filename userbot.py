import asyncio
from telethon import TelegramClient, events
from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException
import config

client = TelegramClient("userbot_session", config.API_ID, config.API_HASH)
translator = GoogleTranslator(source="auto", target="tr")

auto_translate_groups: set[int] = {-5159556768, -5301469268}


def is_english(text: str) -> bool:
    try:
        return detect(text) == "en"
    except LangDetectException:
        return False


def translate(text: str) -> str:
    try:
        return translator.translate(text)
    except Exception as e:
        return f"[Çeviri hatası: {e}]"


# Saved Messages'a forward edilen mesajları çevir
@client.on(events.NewMessage(outgoing=True, chats="me"))
async def forward_translate(event):
    # Forward edilmiş mesaj mı?
    if not event.forward:
        return
    if not event.text or len(event.text.strip()) < 3:
        return

    result = translate(event.text)
    original_lang = ""
    try:
        from langdetect import detect
        lang = detect(event.text)
        if lang == "tr":
            return  # Zaten Türkçe, çevirme
    except:
        pass

    await client.send_message("me", f"🇹🇷 **Çeviri:**\n{result}")


# Otomatik mod: belirlenen gruplardaki İngilizce mesajları Saved Messages'a gönder
@client.on(events.NewMessage(incoming=True))
async def auto_translate_listener(event):
    if event.chat_id not in auto_translate_groups:
        return
    if not event.text or len(event.text.strip()) < 10:
        return
    if not is_english(event.text):
        return

    result = translate(event.text)
    sender = await event.get_sender()
    sender_name = getattr(sender, "first_name", "Bilinmeyen")
    chat = await event.get_chat()
    chat_title = getattr(chat, "title", str(event.chat_id))

    pm_text = (
        f"📨 **{chat_title}** — {sender_name}\n"
        f"🇬🇧 {event.text}\n\n"
        f"🇹🇷 {result}"
    )
    await client.send_message("me", pm_text)


async def main():
    print("Userbot başlatılıyor...")
    await client.start()
    print("Userbot çalışıyor!")
    await client.run_until_disconnected()


asyncio.run(main())
