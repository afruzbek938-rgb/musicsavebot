import asyncio
import os
import re
import json
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile
import yt_dlp

# Tokenni to'g'ridan-to'g'ri kodga yozdik
TOKEN = "8936913831:AAE29TdwOI_aRKdIM2I2Njn71ma3umAWHbY"
ADMIN_ID = 6949980794 
USER_NAMES_FILE = "user_names.json"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

def load_users():
    if os.path.exists(USER_NAMES_FILE):
        with open(USER_NAMES_FILE, "r") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_user(user_id, name):
    users = load_users()
    users[str(user_id)] = name
    with open(USER_NAMES_FILE, "w") as f:
        json.dump(users, f)

@dp.message(F.text.startswith("/reklama "))
async def broadcast(message: Message):
    if message.from_user.id != ADMIN_ID: return
    text = message.text.replace("/reklama ", "")
    users = load_users()
    for user_id in users.keys():
        try:
            await bot.send_message(chat_id=int(user_id), text=text)
            await asyncio.sleep(0.05)
        except: pass
    await message.answer("✅ Reklama yuborildi.")

@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    save_user(message.from_user.id, message.from_user.first_name)
    await message.answer("🎧 Salom! Qo'shiq nomini yozing:")

@dp.message(F.text)
async def handle_music(message: Message):
    save_user(message.from_user.id, message.from_user.first_name)
    wait_msg = await message.answer("⏳ Qidirilmoqda...")
    
    cleaned_text = re.sub(r'[^\w\s\-]', '', message.text).strip()
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "quiet": True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{cleaned_text}", download=True)
            entry = info["entries"][0]
            file_path = f"downloads/{entry['id']}.{entry.get('ext', 'mp3')}"
            
            await message.answer_audio(
                audio=FSInputFile(file_path),
                caption=f"🎼 <b>{entry['title']}</b>",
                duration=int(entry.get("duration", 0))
            )
            if os.path.exists(file_path): os.remove(file_path)
    except:
        await message.answer("❌ Qo'shiq topilmadi!")
    await wait_msg.delete()

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
