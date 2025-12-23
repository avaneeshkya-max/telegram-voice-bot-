from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler
)
from gtts import gTTS
from langdetect import detect
import os, time, subprocess, math

import os
BOT_TOKEN = os.getenv("BOT_TOKEN")

user_lang = {}
user_voice = {}

LANGS = {
    "Hindi 🇮🇳": "hi",
    "English 🇺🇸": "en",
    "Urdu 🇵🇰": "ur",
    "Arabic 🇸🇦": "ar",
    "French 🇫🇷": "fr",
    "Spanish 🇪🇸": "es",
    "Russian 🇷🇺": "ru",
    "Japanese 🇯🇵": "ja",
    "Korean 🇰🇷": "ko",
    "German 🇩🇪": "de"
}

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🗣️ Male Voice", callback_data="voice_male"),
         InlineKeyboardButton("🗣️ Female Voice", callback_data="voice_female")],
        [InlineKeyboardButton("🌍 Select Language", callback_data="lang_menu")]
    ]
    update.message.reply_text(
        "👋 Welcome! Send your text below 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def buttons(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    data = query.data
    cid = query.message.chat_id

    if data.startswith("voice_"):
        user_voice[cid] = data.split("_")[1]
        query.message.reply_text("✅ Voice selected!")

    elif data == "lang_menu":
        kb = [[InlineKeyboardButton(name, callback_data=f"lang_{code}")]
              for name, code in LANGS.items()]
        query.message.reply_text(
            "🌍 Language select karo:",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif data.startswith("lang_"):
        user_lang[cid] = data.split("_")[1]
        query.message.reply_text("✅ Language selected!")

def split_text(text, max_len=4500):
    return [text[i:i+max_len] for i in range(0, len(text), max_len)]

def text_to_voice(update: Update, context: CallbackContext):
    try:
        chat_id = update.message.chat_id
        text = update.message.text

        update.message.reply_text("🎙️ Generating your voice...")
        time.sleep(2)

        lang = user_lang.get(chat_id)
        if not lang:
            try:
                lang = detect(text)
            except:
                lang = "en"

        parts = split_text(text)

        for i, part in enumerate(parts):
            mp3 = f"{chat_id}_{i}.mp3"
            ogg = f"{chat_id}_{i}.ogg"

            tts = gTTS(text=part, lang=lang)
            tts.save(mp3)

            subprocess.call(
                ["ffmpeg", "-y", "-i", mp3, "-c:a", "libopus", ogg],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            context.bot.send_voice(
                chat_id=chat_id,
                voice=open(ogg, "rb")
            )

            os.remove(mp3)
            os.remove(ogg)

    except Exception as e:
        update.message.reply_text("❌ Error aaya hai, phir se try karein!")
        print(e)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(buttons))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, text_to_voice))

    updater.start_polling()
    print("🤖 Ultimate Voice Bot Running...")
    updater.idle()

if __name__ == "__main__":
    main()