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

# Bot konfiguratsiyasi
TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQ"
USER_DATA_FILE = "users.json"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Ma'lumotlarni yuklash va saqlash
def load_data():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def save_user_data(user_id, lang):
    users = load_data()
    users[str(user_id)] = lang
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f)

# Klaviatura
def lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz"),
         InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])

@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer("Tilni tanlang / Выберите язык / Select language:", reply_markup=lang_keyboard())

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(call: CallbackQuery):
    lang = call.data.split("_")[1]
    save_user_data(call.from_user.id, lang)
    await call.message.edit_text("Til saqlandi! Qo'shiq nomini yozing." if lang == "uz" else 
                                 ("Язык сохранен! Введите название." if lang == "ru" else "Language saved! Send song name."))

@dp.message(F.text)
async def handle_music(message: Message):
    users = load_data()
    lang = users.get(str(message.from_user.id), "uz")
    
    wait_msg = await message.answer("⏳ Qidirilmoqda..." if lang == "uz" else "⏳ Поиск..." if lang == "ru" else "⏳ Searching...")
    
    cleaned_text = re.sub(r'[^\w\s\-]', '', message.text).strip()
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "quiet": True
    }
    
    try:
        # yt_dlp ishlashi uchun loop kerak
        loop = asyncio.get_event_loop()
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(f"ytsearch1:{cleaned_text}", download=True)
        
        info = await loop.run_in_executor(None, download)
        entry = info["entries"][0]
        file_path = f"downloads/{entry['id']}.{entry.get('ext', 'mp3')}"
        
        await message.answer_audio(
            audio=FSInputFile(file_path),
            caption=f"🎼 <b>{entry['title']}</b>\n\n🎧 @Music_Saved_bot",
            duration=int(entry.get("duration", 0))
        )
        # Faylni o'chirish
        if os.path.exists(file_path): os.remove(file_path)
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await message.answer("❌ Xatolik yuz berdi yoki qo'shiq topilmadi!" if lang == "uz" else "❌ Ошибка или песня не найдена!" if lang == "ru" else "❌ Error or song not found!")
    finally:
        await wait_msg.delete()

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
