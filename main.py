import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
import yt_dlp

TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQ"
dp = Dispatcher()

# Eng muhim qism: YouTube bot ekanligimizni sezmasligi uchun sozlamalar
def get_ydl_opts(filename):
    return {
        "format": "bestaudio/best",
        "outtmpl": filename,
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "default_search": "ytsearch1:", # YouTube'dan faqat eng mosini qidiradi
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

async def search_and_download(query):
    filename = "downloads/audio.mp3"
    # Eski fayllarni o'chiramiz
    if os.path.exists(filename): os.remove(filename)
    
    try:
        with yt_dlp.YoutubeDL(get_ydl_opts(filename)) as ydl:
            # Qidiruvni aniqlashtirish: "audio" kalit so'zi qo'shildi
            info = ydl.extract_info(f"ytsearch1:{query} audio", download=True)
            if 'entries' in info and info['entries']:
                return info['entries'][0].get('title', query)
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

@dp.message(F.text)
async def handle_message(msg: Message):
    wait_msg = await msg.reply("🎧 Qidirilmoqda...")
    
    title = await search_and_download(msg.text)
    file_path = "downloads/audio.mp3"
    
    if title and os.path.exists(file_path):
        # Fayl nomi va performer qismi
        await msg.reply_audio(
            audio=FSInputFile(file_path),
            caption=f"🎧 {title}\n\n━━━━━━━━━━━━\n@Mucis_Saved_bot",
            title=title,
            performer="Mucis_Saved_bot"
        )
        await wait_msg.delete()
        os.remove(file_path)
    else:
        await wait_msg.edit_text("❌ Topilmadi. Iltimos, xonanda va qo'shiq nomini to'liq yozing.")

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
