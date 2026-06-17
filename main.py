import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
import yt_dlp

TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQ"
dp = Dispatcher()

# Qidiruv tizimini o'zgartiramiz
YDL_OPTS = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "nocheckcertificate": True,
    "default_search": "ytsearch1:", # YouTube ichidan qidirish
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

async def search_and_download(query):
    # Qidiruvni kuchaytirish uchun "official audio" so'zini qo'shamiz
    search_query = f"ytsearch1:{query} official audio"
    try:
        with yt_dlp.YoutubeDL({**YDL_OPTS, "outtmpl": "downloads/song.mp3"}) as ydl:
            info = ydl.extract_info(search_query, download=True)
            return "downloads/song.mp3" if info else None
    except Exception as e:
        print(f"Xato: {e}")
        return None

@dp.message(F.text)
async def handle_message(msg: Message):
    wait_msg = await msg.reply("🎧 Qidirilmoqda...")
    
    file_path = await search_and_download(msg.text)
    
    if file_path and os.path.exists(file_path):
        await msg.reply_audio(audio=FSInputFile(file_path), caption="@Mucis_Saved_bot")
        os.remove(file_path)
        await wait_msg.delete()
    else:
        await wait_msg.edit_text("❌ Topilmadi. Iltimos, boshqacharoq yozib ko'ring (masalan: 'Jony - Kometa').")

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
