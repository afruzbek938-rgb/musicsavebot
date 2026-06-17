import asyncio
import os
import re
import gc
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import yt_dlp

TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQ"
dp = Dispatcher()

# Xavfsiz yuklash sozlamalari
def get_ydl_opts(mode='video'):
    return {
        "format": "best[ext=mp4][height<=720]/best" if mode == 'video' else "bestaudio/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

async def download_media(url, mode='video'):
    loop = asyncio.get_running_loop()
    try:
        def run_dl():
            with yt_dlp.YoutubeDL(get_ydl_opts(mode)) as ydl:
                return ydl.extract_info(url, download=True)
        
        info = await loop.run_in_executor(None, run_dl)
        return info
    except Exception as e:
        print(f"DL ERROR: {e}")
        return None
    finally:
        gc.collect()

@dp.message(F.text.startswith("http"))
async def handle_url(message: Message):
    url = message.text
    wait_msg = await message.reply("⏳ *Yuklanmoqda...*", parse_mode=ParseMode.MARKDOWN)
    
    info = await download_media(url, mode='video')
    
    if info:
        file_path = f"downloads/{info['id']}.{info.get('ext', 'mp4')}"
        if os.path.exists(file_path):
            kb = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🎵 MP3 ga o'girish", callback_data=f"mp3_{info['id']}")
            ]])
            await message.reply_video(video=FSInputFile(file_path), caption=f"📹 {info.get('title', 'Video')}", reply_markup=kb)
            await wait_msg.delete()
            # Faylni biroz vaqtdan keyin o'chirish uchun (server xotirasi uchun)
            asyncio.create_task(delayed_delete(file_path))
        else:
            await wait_msg.edit_text("❌ Fayl topilmadi.")
    else:
        await wait_msg.edit_text("❌ Yuklashda xatolik. Havola noto'g'ri bo'lishi mumkin.")

async def delayed_delete(path):
    await asyncio.sleep(60) # 1 daqiqa saqlaydi
    if os.path.exists(path): os.remove(path)

@dp.callback_query(F.data.startswith("mp3_"))
async def convert_to_mp3(callback: CallbackQuery):
    await callback.answer("⏳ MP3 tayyorlanmoqda...")
    video_id = callback.data.split("_")[1]
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    info = await download_media(url, mode='audio')
    if info:
        file_path = f"downloads/{info['id']}.{info.get('ext', 'mp3')}"
        await callback.message.reply_audio(audio=FSInputFile(file_path), title=info.get('title'))
        os.remove(file_path)
    else:
        await callback.message.answer("❌ Audio yuklashda xato.")

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
