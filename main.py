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

TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQ"
ADMIN_ID = 6949980794 
USER_DATA_FILE = "users.json" # Foydalanuvchi tili va ismi saqlanadi

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Foydalanuvchi ma'lumotlarini boshqarish
def load_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_user_data(user_id, data):
    users = load_data()
    users[str(user_id)] = data
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f)

# Til tanlash uchun klaviatura
def lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz"),
         InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])

@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer(f"Assalomu alaykum, {message.from_user.first_name}! Tilni tanlang:\nВыберите язык:\nSelect language:", reply_markup=lang_keyboard())

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(call: CallbackQuery):
    lang = call.data.split("_")[1]
    save_user_data(call.from_user.id, {"name": call.from_user.first_name, "lang": lang})
    await call.message.edit_text(f"Til saqlandi! Qo'shiq nomini yozing." if lang == "uz" else 
                                 ("Язык сохранен! Введите название песни." if lang == "ru" else "Language saved! Send song name."))

@dp.message(F.text)
async def handle_music(message: Message):
    user_data = load_data().get(str(message.from_user.id))
    if not user_data:
        await message.answer("Iltimos, /start buyrug'ini bosing.")
        return

    wait_msg = await message.answer("⏳...")
    cleaned_text = re.sub(r'[^\w\s\-]', '', message.text).strip()
    
    ydl_opts = {"format": "bestaudio/best", "noplaylist": True, "outtmpl": "downloads/%(id)s.%(ext)s", "quiet": True}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{cleaned_text}", download=True)
            entry = info["entries"][0]
            file_path = f"downloads/{entry['id']}.{entry.get('ext', 'mp3')}"
            
            # Imzo bilan yuborish
            caption = f"🎼 <b>{entry['title']}</b>\n\n🎧 @Music_Saved_bot"
            
            await message.answer_audio(
                audio=FSInputFile(file_path),
                caption=caption,
                duration=int(entry.get("duration", 0))
            )
            if os.path.exists(file_path): os.remove(file_path)
    except:
        await message.answer("❌ Qo'shiq topilmadi!" if user_data['lang'] == "uz" else "❌ Песня не найдена!" if user_data['lang'] == "ru" else "❌ Song not found!")
    await wait_msg.delete()

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
