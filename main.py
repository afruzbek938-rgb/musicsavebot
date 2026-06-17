import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
import yt_dlp

TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQE"
dp = Dispatcher()

# Video yuklash funksiyasi
async def download_media(url):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/song.mp3",
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return info.get('title', 'Audio')
    except:
        return None

@dp.message(F.text.startswith("http"))
async def handle_url(msg: Message):
    wait_msg = await msg.reply("🎧 Yuklanmoqda, kuting...")
    
    title = await download_media(msg.text)
    file_path = "downloads/song.mp3"
    
    if title and os.path.exists(file_path):
        await msg.reply_audio(
            audio=FSInputFile(file_path),
            caption=f"🎧 {title}\n\n━━━━━━━━━━━━\n@Mucis_Saved_bot",
            title=title,
            performer="Mucis_Saved_bot"
        )
        await wait_msg.delete()
        if os.path.exists(file_path): os.remove(file_path)
    else:
        await wait_msg.edit_text("❌ Yuklashda xatolik. Havolani tekshiring.")

@dp.message(F.text)
async def handle_text(msg: Message):
    # Agar foydalanuvchi link emas, shunchaki matn yozsa:
    await msg.reply("⚠️ **Qidiruv tizimi cheklangan.**\n\nIltimos, menga YouTube-dan musiqaning **linkini** (havolasini) yuboring.")

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
