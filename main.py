import asyncio
import os
import json
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import yt_dlp

TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQ"
ADMIN_ID = 6949980794
USER_DATA_FILE = "users.json"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- BAZA BILAN ISHLASH ---
def load_data():
    if not os.path.exists(USER_DATA_FILE): return {}
    with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return {}

def save_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# --- MENYU (Inline) ---
def get_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz"),
         InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="💎 Mening limitim", callback_data="show_limit")]
    ])

# --- BUYRUQLAR ---
@dp.message(F.text.in_({"/start", "/", "/menu"}))
async def cmd_start(message: Message):
    await message.answer(f"Assalomu alaykum, <b>{message.from_user.first_name}</b>!\nTilni tanlang yoki limitni ko'ring:", reply_markup=get_menu())

@dp.message(F.text == "/admin")
async def admin_cmd(message: Message):
    if message.from_user.id == ADMIN_ID:
        users = load_data()
        await message.answer(f"🛠 Admin panel.\n👥 Foydalanuvchilar soni: {len(users)}")
    else:
        await message.answer("❌ Siz admin emassiz!")

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(call: CallbackQuery):
    lang = call.data.split("_")[1]
    users = load_data()
    uid = str(call.from_user.id)
    if uid not in users: users[uid] = {"limit": 50, "lang": lang}
    else: users[uid]["lang"] = lang
    save_data(users)
    await call.message.edit_text(f"✅ Til: {lang.upper()}. Endi musiqa nomini yozing.")

@dp.callback_query(F.data == "show_limit")
async def show_limit(call: CallbackQuery):
    users = load_data()
    uid = str(call.from_user.id)
    limit = users.get(uid, {}).get("limit", 50)
    await call.message.answer(f"💎 Sizning qolgan limitingiz: <b>{limit}</b> ta.")

# --- MUSIQA YUKLASH (Asosiy funksiya) ---
@dp.message(F.text & ~F.text.startswith("/"))
async def handle_music(message: Message):
    users = load_data()
    uid = str(message.from_user.id)
    if uid not in users:
        await message.answer("Iltimos, avval /start ni bosing.")
        return
    if users[uid]["limit"] <= 0:
        await message.answer("❌ Limitingiz tugadi.")
        return

    wait = await message.answer("⏳ Qidirilmoqda...")
    
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "quiet": True,
        "default_search": "ytsearch1",
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
        "addmetadata": False,
        "writethumbnail": False
    }
    
    try:
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(message.text, download=True)
                return info['entries'][0] if 'entries' in info else info
        
        info = await asyncio.to_thread(download)
        path = f"downloads/{info['id']}.mp3"
        
        if os.path.exists(path):
            await message.answer_audio(audio=FSInputFile(path), caption=f"🎵 {info['title']}")
            users[uid]["limit"] -= 1
            save_data(users)
            os.remove(path)
        else:
            await message.answer("❌ Topilmadi.")
    except Exception as e:
        await message.answer("❌ Yuklashda xatolik.")
    await wait.delete()

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
