import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
import yt_dlp

TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQ"
dp = Dispatcher()

# Eng muhim sozlama: ffmpeg-siz yuklash
YDL_OPTS = {
    "format": "bestaudio/best",
    "outtmpl": "downloads/audio.mp3",
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True
}

async def download_audio(url):
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=True)
            return info.get('title', 'Audio')
    except: return None

@dp.message(F.text.startswith("http"))
async def handle_url(msg: Message):
    wait_msg = await msg.reply("⏳ Yuklanmoqda...")
    title = await download_audio(msg.text)
    file_path = "downloads/audio.mp3"
    
    if title and os.path.exists(file_path):
        await msg.reply_audio(audio=FSInputFile(file_path), caption=f"🎧 {title}")
        await wait_msg.delete()
        os.remove(file_path)
    else:
        await wait_msg.edit_text("❌ Xatolik. Havola noto'g'ri yoki botda muammo bor.")

@dp.message()
async def echo(msg: Message):
    await msg.reply("Iltimos, YouTube yoki boshqa sayt havolasini yuboring (link).")

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
