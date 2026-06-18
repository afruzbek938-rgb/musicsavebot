import asyncio
import os
import json
import logging
import re
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import yt_dlp

TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQ"
USER_DATA_FILE = "users.json"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Tarjimalar
LANGS = {
    "uz": {"greet": "Assalomu alaykum, {name}! Til saqlandi, qo'shiq nomini yozing.", "search": "⏳ Qidirilmoqda...", "not_found": "❌ Qo'shiq topilmadi!"},
    "ru": {"greet": "Здравствуйте, {name}! Язык сохранен, введите название песни.", "search": "⏳ Поиск...", "not_found": "❌ Песня не найдена!"},
    "en": {"greet": "Hello, {name}! Language saved, enter the song name.", "search": "⏳ Searching...", "not_found": "❌ Song not found!"}
}

def load_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_user_data(user_id, lang):
    users = load_data()
    users[str(user_id)] = lang
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f)

@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    name = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz"),
         InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])
    await message.answer(f"Salom {name}! Tilni tanlang / Выберите язык / Select language:", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(call: CallbackQuery):
    lang = call.data.split("_")[1]
    save_user_data(call.from_user.id, lang)
    name = f'<a href="tg://user?id={call.from_user.id}">{call.from_user.first_name}</a>'
    await call.message.edit_text(LANGS[lang]["greet"].format(name=name))

@dp.message(F.text)
async def handle_music(message: Message):
    users = load_data()
    user_id_str = str(message.from_user.id)
    lang = users.get(user_id_str, "uz")
    
    if user_id_str not in users:
        await message.answer("Iltimos, avval /start buyrug'ini bosing.")
        return

    wait_msg = await message.answer(LANGS[lang]["search"])
    
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "quiet": True,
        "default_search": "ytsearch1"
    }
    
    try:
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(message.text, download=True)
        
        info = await asyncio.to_thread(download)
        entry = info["entries"][0]
        file_path = f"downloads/{entry['id']}.{entry.get('ext', 'mp3')}"
        
        # Fayl nomi toza bo'lishi uchun belgilar tozalanadi
        clean_title = re.sub(r'[\\/*?:"<>|]', "", entry['title'])
        
        await message.answer_audio(
            audio=FSInputFile(file_path, filename=f"{clean_title}.mp3"),
            caption=f"🎼 <b>{entry['title']}</b>\n\n🎧 @Music_Saved_bot",
            duration=int(entry.get("duration", 0))
        )
        if os.path.exists(file_path): os.remove(file_path)
    except Exception as e:
        logging.error(f"Xato: {e}")
        await message.answer(LANGS[lang]["not_found"])
    
    await wait_msg.delete()

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    print("🚀 Bot @Music_Saved_bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
