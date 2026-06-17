import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
import yt_dlp

TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQ"
dp = Dispatcher()

# Eng muhim qismi - qidiruv sozlamalari
def get_ydl_opts():
    return {
        "format": "bestaudio/best",
        "outtmpl": "downloads/song.mp3",
        "quiet": True,
        "nocheckcertificate": True,
        "default_search": "ytsearch1:", # Aynan bitta natijani topadi
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

async def search_and_download(query):
    try:
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            # "official audio" qo'shish qidiruvni aniqroq qiladi
            info = ydl.extract_info(f"ytsearch1:{query} official audio", download=True)
            return True
    except:
        return False

@dp.message(F.text)
async def handle_message(msg: Message):
    wait_msg = await msg.reply("🔍 Qidirilmoqda...")
    
    success = await search_and_download(msg.text)
    file_path = "downloads/song.mp3"
    
    if success and os.path.exists(file_path):
        await msg.reply_audio(
            audio=FSInputFile(file_path),
            caption=f"🎧 {msg.text}\n\n@Mucis_Saved_bot",
            title=msg.text,
            performer="Mucis_Saved_bot"
        )
        await wait_msg.delete()
        os.remove(file_path)
    else:
        await wait_msg.edit_text("❌ Topilmadi. Boshqa nom bilan urinib ko'ring (masalan: 'Jony Kometa').")

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
