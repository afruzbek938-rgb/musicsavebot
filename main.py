import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
import yt_dlp

TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQ"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Qidiruv funksiyasi
async def download_audio(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "default_search": "ytsearch1:",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "quiet": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        entry = info["entries"][0]
        return f"downloads/{entry['id']}.{entry.get('ext', 'mp3')}", entry['title']

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Salom! Qo'shiq nomini yozing, men uni yuklab beraman.")

@dp.message(F.text)
async def handle_message(message: Message):
    try:
        wait_msg = await message.answer("⏳ Yuklanmoqda...")
        file_path, title = await download_audio(message.text)
        await message.answer_audio(audio=FSInputFile(file_path), caption=f"🎼 {title}")
        if os.path.exists(file_path): os.remove(file_path)
        await wait_msg.delete()
    except Exception as e:
        await message.answer(f"Xatolik: {e}")

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    print("Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
