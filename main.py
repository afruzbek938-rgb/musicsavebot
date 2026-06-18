import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile
import yt_dlp

TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQ"
ADMIN_ID = 6949980794  # Sizning IDingiz

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(F.text == "/admin")
async def admin_panel(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🛠 <b>Admin panelga xush kelibsiz!</b>\n\nBot hozirda mukammal ishlamoqda.")
    else:
        await message.answer("❌ Siz admin emassiz!")

@dp.message(F.text)
async def handle_music(message: Message):
    # Admin bo'lsa yoki oddiy foydalanuvchi bo'lsa
    wait_msg = await message.answer("⏳ Qidirilmoqda...")
    
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "quiet": True,
        "default_search": "ytsearch1",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "writethumbnail": False,
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
            await message.answer("❌ Fayl topilmadi.")
            
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await message.answer("❌ Kechirasiz, bu musiqani yuklab bo'lmadi.")
    
    await wait_msg.delete()

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    print("🚀 Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
