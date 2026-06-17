import asyncio
import os
import re
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile
import yt_dlp

# Tokeningiz
TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQ"
dp = Dispatcher()

# yt-dlp sozlamalari - CRASH bo'lmasligi uchun xavfsiz qilib yozildi
def get_ydl_opts(filename):
    return {
        "format": "bestaudio/best",
        "outtmpl": filename,
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

async def search_and_download(query):
    # Fayl nomi
    filename = "downloads/song.mp3"
    # Eski faylni o'chiramiz
    if os.path.exists(filename): os.remove(filename)
    
    try:
        with yt_dlp.YoutubeDL(get_ydl_opts(filename)) as ydl:
            # Qidiruv so'rovi
            search_query = f"ytsearch1:{query} official audio"
            info = ydl.extract_info(search_query, download=True)
            if 'entries' in info and info['entries']:
                return info['entries'][0].get('title', query)
            return None
    except Exception as e:
        print(f"Xato: {e}")
        return None

@dp.message(F.text == "/start")
async def start(msg: Message):
    await msg.reply("Salom! Qo'shiq nomini yozing, men uni topib beraman.")

@dp.message(F.text)
async def handle_message(msg: Message):
    wait_msg = await msg.reply("🎧 Qidirilmoqda...")
    
    song_title = await search_and_download(msg.text)
    file_path = "downloads/song.mp3"
    
    if song_title and os.path.exists(file_path):
        await msg.reply_audio(
            audio=FSInputFile(file_path),
            caption=f"🎧 {msg.text}\n\n━━━━━━━━━━━━\n@Mucis_Saved_bot",
            title=msg.text,
            performer="Mucis_Saved_bot"
        )
        await wait_msg.delete()
    else:
        await wait_msg.edit_text("❌ Topilmadi. Iltimos, boshqacharoq yozib ko'ring (masalan: 'Jony - Kometa').")

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
