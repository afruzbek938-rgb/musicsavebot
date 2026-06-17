import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
import yt_dlp

# Tokeningiz
TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQ"
dp = Dispatcher()

# Eng muhim sozlama: qidiruv yo'q, faqat yuklash
async def download_from_link(url):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/audio.mp3",
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            return True
    except:
        return False

@dp.message(F.text.startswith("http"))
async def handle_link(msg: Message):
    wait = await msg.reply("⏳ Yuklanmoqda...")
    if await download_from_link(msg.text):
        await msg.reply_audio(audio=FSInputFile("downloads/audio.mp3"), caption="@Mucis_Saved_bot")
        os.remove("downloads/audio.mp3")
        await wait.delete()
    else:
        await wait.edit_text("❌ Yuklashda xatolik. Linkni tekshiring.")

@dp.message()
async def echo(msg: Message):
    await msg.reply("⚠️ **Qidiruv funksiyasi o'chirilgan.**\n\nIltimos, shunchaki YouTube yoki Instagram havolasini (link) yuboring.")

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
