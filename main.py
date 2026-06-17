import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
import yt_dlp

TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQ"
dp = Dispatcher()

# Eng muhim sozlama: ffmpeg-siz yuklash (Crashed bo'lmasligi uchun)
YDL_OPTS = {
    "format": "bestaudio/best",
    "outtmpl": "downloads/audio.mp3",
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True
}

async def download_audio(query):
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            # Qidiruvni aniqroq qilish
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            return True
    except: 
        return False

@dp.message(F.text)
async def handle_message(msg: Message):
    wait_msg = await msg.reply("⏳ Qidirilmoqda...")
    
    success = await download_audio(msg.text)
    file_path = "downloads/audio.mp3"
    
    if success and os.path.exists(file_path):
        await msg.reply_audio(audio=FSInputFile(file_path), caption=f"🎧 {msg.text}")
        await wait_msg.delete()
        os.remove(file_path)
    else:
        await wait_msg.edit_text("❌ Topilmadi. Iltimos, boshqacharoq yozib ko'ring (masalan: 'Jony Kometa').")

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
