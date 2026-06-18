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

LANGS = {
    "uz": {"greet": "Til saqlandi! Qo'shiq nomini yozing.", "search": "⏳ Qidirilmoqda...", "not_found": "❌ Qo'shiq topilmadi!"},
    "ru": {"greet": "Язык сохранен! Введите название.", "search": "⏳ Поиск...", "not_found": "❌ Не найдено!"},
    "en": {"greet": "Language saved! Send song name.", "search": "⏳ Searching...", "not_found": "❌ Not found!"}
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
        [InlineKeyboardButton(text="🇺🇿 O'z", callback_data="lang_uz"),
         InlineKeyboardButton(text="🇷🇺 Ru", callback_data="lang_ru"),
         InlineKeyboardButton(text="🇬🇧 En", callback_data="lang_en")]
    ])
    await message.answer(f"Assalomu alaykum {name}! Tilni tanlang:", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(call: CallbackQuery):
    lang = call.data.split("_")[1]
    save_user_data(call.from_user.id, lang)
    await call.message.edit_text(LANGS[lang]["greet"])

@dp.message(F.text)
async def handle_music(message: Message):
    users = load_data()
    lang = users.get(str(message.from_user.id), "uz")
    
    wait_msg = await message.answer(LANGS[lang]["search"])
    
    # Qidiruv sozlamalarini yangiladik (yt-dlp uchun optimal)
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "quiet": True,
        "default_search": "ytsearch1",
        "nocheckcertificate": True, # SSL xatoliklarini oldini oladi
        "user_agent": "Mozilla/5.0"
    }
    
    try:
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(message.text, download=True)
        
        info = await asyncio.to_thread(download)
        
        # 'entries' mavjudligini tekshiramiz
        if "entries" in info and info["entries"]:
            entry = info["entries"][0]
            file_path = f"downloads/{entry['id']}.{entry.get('ext', 'mp3')}"
            clean_title = re.sub(r'[\\/*?:"<>|]', "", entry['title'])
            
            await message.answer_audio(
                audio=FSInputFile(file_path, filename=f"{clean_title}.mp3"),
                caption=f"🎼 <b>{entry['title']}</b>", # Bot nomi olib tashlandi
                duration=int(entry.get("duration", 0))
            )
            if os.path.exists(file_path): os.remove(file_path)
        else:
            await message.answer(LANGS[lang]["not_found"])
            
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await message.answer(LANGS[lang]["not_found"])
    
    await wait_msg.delete()

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    print("🚀 Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
