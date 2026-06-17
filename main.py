import asyncio
import os
import json
import re
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.filters import Command
import yt_dlp

TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQ"
bot = Bot(token=TOKEN)
dp = Dispatcher()
LANG_FILE = "user_langs.json"

def clean_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def load_langs():
    if os.path.exists(LANG_FILE):
        with open(LANG_FILE, "r") as f: return json.load(f)
    return {}

user_langs = load_langs()

def get_lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"),
         InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])

@dp.message(Command("start"))
async def start(message: Message):
    name = message.from_user.first_name
    await message.answer(f"Salom, {name}! 🎧\nTilni tanlang / Выберите язык / Select language:", reply_markup=get_lang_kb())

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    user_langs[str(callback.from_user.id)] = lang
    with open(LANG_FILE, "w") as f: json.dump(user_langs, f)
    await callback.message.edit_text({"uz": "Til tanlandi! Qo'shiq nomini yozing.", "ru": "Язык выбран! Введите название песни.", "en": "Language selected! Send song name."}[lang])

@dp.message(F.text)
async def handle_music(message: Message):
    lang = user_langs.get(str(message.from_user.id), "en")
    wait = await message.answer("⏳ Qidirilmoqda...")
    
    # Qidiruv parametrlarini kuchaytiramiz
    ydl_opts = {
        "format": "bestaudio/best",
        "default_search": "ytsearch1:",
        "quiet": True,
        "nocheckcertificate": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "outtmpl": "downloads/temp.%(ext)s"
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Qidiruv so'rovi yanada aniqroq qilindi
            info = ydl.extract_info(f"ytsearch1:{message.text} song", download=True)
            
            if 'entries' not in info or not info['entries']:
                raise Exception("Topilmadi")
                
            entry = info["entries"][0]
            real_title = clean_filename(entry['title'])
            file_path = f"downloads/{real_title}.mp3"
            
            ext = entry.get('ext', 'mp3')
            os.rename(f"downloads/temp.{ext}", file_path)
            
            caption = f"🎧 {real_title}\n\n━━━━━━━━━━━━\n@Mucis_Saved_bot"
            
            await message.answer_audio(
                audio=FSInputFile(file_path), 
                caption=caption
            )
            
            if os.path.exists(file_path): os.remove(file_path)
    except Exception as e:
        await message.answer({"uz": "❌ Topilmadi, boshqa nom bilan urinib ko'ring!", "ru": "❌ Не найдено, попробуйте другое название!", "en": "❌ Not found, try another name!"}[lang])
    
    await wait.delete()

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
