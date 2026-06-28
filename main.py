import asyncio
import os
import re
import json
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import yt_dlp

TOKEN = "8936913831:AAE29TdwOI_aRKdIM2I2Njn71ma3umAWHbY"
USER_DATA_FILE = "users.json"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Tarjimalar lug'ati
LANGS = {
    "uz": {"greet": "Assalomu alaykum, {name}! Til saqlandi, qo'shiq nomini yozing.", "search": "⏳ Qidirilmoqda..."},
    "ru": {"greet": "Здравствуйте, {name}! Язык сохранен, введите название песни.", "search": "⏳ Поиск..."},
    "en": {"greet": "Hello, {name}! Language saved, enter the song name.", "search": "⏳ Searching..."}
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
    # Rangli ism formatlash
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
    lang = users.get(str(message.from_user.id), "uz")
    
    wait_msg = await message.answer(LANGS[lang]["search"])
    
    cleaned_text = re.sub(r'[^\w\s\-]', '', message.text).strip()
    ydl_opts = {"format": "bestaudio/best", "noplaylist": True, "outtmpl": "downloads/%(id)s.%(ext)s", "quiet": True}
    
    try:
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(f"ytsearch1:{cleaned_text}", download=True)
        
        info = await asyncio.to_thread(download)
        entry = info["entries"][0]
        file_path = f"downloads/{entry['id']}.{entry.get('ext', 'mp3')}"
        
        # Rasmda ko'rsatilganidek formatda yuborish (image_9ff8c9.png)
        caption = f"🎼 <b>{entry['title']}</b>\n\n🎧 @Music_Saved_bot"
        
        await message.answer_audio(audio=FSInputFile(file_path), caption=caption, duration=int(entry.get("duration", 0)))
        if os.path.exists(file_path): os.remove(file_path)
    except:
        await message.answer("❌ Xatolik!")
    await wait_msg.delete()

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
