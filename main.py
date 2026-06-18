import asyncio
import os
import json
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
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

# --- MENYU ---
def get_main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🎵 Musiqa yuklash")],
        [KeyboardButton(text="💎 Mening limitim"), KeyboardButton(text="🔗 Taklif qilish")]
    ], resize_keyboard=True)

# --- BUYRUQLAR ---
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    users = load_data()
    user_id = str(message.from_user.id)
    
    if user_id not in users:
        users[user_id] = {"lang": "uz", "limit": 50, "referred": False}
        save_data(users)
        await message.answer("Xush kelibsiz! Sizga 50 ta limit berildi.", reply_markup=get_main_menu())
    else:
        await message.answer("Bosh menyu:", reply_markup=get_main_menu())

@dp.message(F.text == "💎 Mening limitim")
async def check_limit(message: Message):
    users = load_data()
    limit = users.get(str(message.from_user.id), {}).get("limit", 0)
    await message.answer(f"Sizning qolgan limitingiz: <b>{limit}</b> ta")

@dp.message(F.text == "🔗 Taklif qilish")
async def get_referal(message: Message):
    bot_info = await bot.get_me()
    await message.answer(f"Do'stlaringizni taklif qiling va 50 ta limitga ega bo'ling!\n\n🔗 Havolangiz: https://t.me/{bot_info.username}?start={message.from_user.id}")

@dp.message(F.text == "🎵 Musiqa yuklash")
async def music_prompt(message: Message):
    await message.answer("Musiqa nomini yozing:")

# --- MUSIQA YUKLASH ---
@dp.message(F.text)
async def handle_music(message: Message):
    if message.text in ["🎵 Musiqa yuklash", "💎 Mening limitim", "🔗 Taklif qilish"]: return
    
    users = load_data()
    user_id = str(message.from_user.id)
    
    if user_id not in users:
        await message.answer("Iltimos, /start ni bosing.")
        return

    if users[user_id]["limit"] <= 0:
        await message.answer("❌ Limitingiz tugadi! Do'stingizni taklif qiling.")
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
            await message.answer_audio(audio=FSInputFile(file_path), caption=f"🎵 {info['title']}")
            users[user_id]["limit"] -= 1
            save_data(users)
            os.remove(file_path)
        else:
            await message.answer("❌ Topilmadi.")
    except Exception as e:
        await message.answer("❌ Yuklashda xatolik.")
    
    await wait_msg.delete()

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
