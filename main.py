import asyncio
import os
import json
import logging
import re
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
import yt_dlp

TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQ"
ADMIN_ID = 6949980794
USER_DATA_FILE = "users.json"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- FUNKSIYALAR ---
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

# --- BUYRUQLAR ---
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    users = load_data()
    if str(message.from_user.id) in users:
        # Foydalanuvchi allaqachon ro'yxatdan o'tgan bo'lsa
        await message.answer("Salom! Musiqa nomini yozing, yuklab beraman.")
    else:
        # Til tanlash
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz")],
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
        ])
        await message.answer("Assalomu alaykum! Tilni tanlang:", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(call: CallbackQuery):
    lang = call.data.split("_")[1]
    save_user_data(call.from_user.id, lang)
    await call.message.edit_text("✅ Til saqlandi! Endi istalgan musiqa nomini yozing.")

# Admin uchun tugmalar paneli
@dp.message(F.text == "/admin")
async def admin_panel(message: Message):
    if message.from_user.id == ADMIN_ID:
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="⬅️ Ortga")]
        ], resize_keyboard=True)
        await message.answer("🛠 Admin panelga xush kelibsiz!", reply_markup=kb)
    else:
        await message.answer("❌ Siz admin emassiz!")

@dp.message(F.text == "📊 Statistika")
async def show_stats(message: Message):
    if message.from_user.id == ADMIN_ID:
        users = load_data()
        await message.answer(f"👥 Jami foydalanuvchilar: {len(users)} ta")

@dp.message(F.text == "⬅️ Ortga")
async def go_back(message: Message):
    await message.answer("Bosh menyuga qaytdingiz.", reply_markup=None)

# --- MUSIQA YUKLASH ---
@dp.message(F.text)
async def handle_music(message: Message):
    if message.text in ["📊 Statistika", "⬅️ Ortga", "/start", "/admin"]:
        return

    users = load_data()
    if str(message.from_user.id) not in users:
        await message.answer("Iltimos, avval /start ni bosing.")
        return

    wait_msg = await message.answer("⏳ Qidirilmoqda...")
    
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "quiet": True,
        "default_search": "ytsearch1",
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
        "addmetadata": False,
    }
    
    try:
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(message.text, download=True)
                return info['entries'][0] if 'entries' in info else info
        
        info = await asyncio.to_thread(download)
        file_path = f"downloads/{info['id']}.mp3"
        
        if os.path.exists(file_path):
            await message.answer_audio(
                audio=FSInputFile(file_path),
                caption=f"🎵 <b>{info['title']}</b>"
            )
            os.remove(file_path)
        else:
            await message.answer("❌ Topilmadi. Boshqa nom bilan urinib ko'ring.")
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await message.answer("❌ Yuklashda xatolik yuz berdi.")
    
    await wait_msg.delete()

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    print("🚀 Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
