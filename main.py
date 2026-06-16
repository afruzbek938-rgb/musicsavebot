import asyncio
import os
import json
import re
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.filters import Command
import yt_dlp

# Botingiz tokeni
TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQ"
bot = Bot(token=TOKEN)
dp = Dispatcher()
LANG_FILE = "user_langs.json"

# Fayl nomidagi xavfli belgilarni tozalash (xato chiqmasligi uchun)
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
    # Ism bilan salomlashish
    name = message.from_user.first_name
    await message.answer(f"Salom, {name}! 🎧\nTilni tanlang / Выберите язык / Select language:", reply_markup=get_lang_kb())

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    user_langs[str(callback.from_user.id)] = lang
    with open(LANG_FILE, "w") as f: json.dump(user_langs, f)
    await callback.message.edit_text({"uz": "Til tanlandi! Qo'shiq nomini yuboring.", "ru": "Язык выбран! Отправьте название песни.", "en": "Language selected! Send song name."}[lang])

@dp.message(F.text)
async def handle_music(message: Message):
    lang = user_langs.get(str(message.from_user.id), "en")
    wait = await message.answer("⏳ Qidirilmoqda...")
    
    # Qidiruv parametrlarini aniqroq qilamiz
    ydl_opts = {
        "format": "bestaudio/best",
        "default_search": "ytsearch1:", 
        "outtmpl": "downloads/temp.%(ext)s",
        "quiet": True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Qidiruv so'roviga "audio" qo'shildi
            info = ydl.extract_info(f"ytsearch1:{message.text} audio", download=True)
            entry = info["entries"][0]
            real_title = clean_filename(entry['title'])
            
            # Faylni haqiqiy nomi bilan qayta nomlash
            file_path = f"downloads/{real_title}.mp3"
            os.rename("downloads/temp.webm", file_path) # Webm formatida yuklansa
            
            # Bot atmetkasi bilan yuborish
            await message.answer_audio(
                audio=FSInputFile(file_path), 
                caption=f"🎼 {real_title}\n\n🤖 @Music_Save_Bot"
            )
            # Faylni o'chirish
            if os.path.exists(file_path):
                os.remove(file_path)
    except Exception as e:
        await message.answer({"uz": "❌ Topilmadi!", "ru": "❌ Не найдено!", "en": "❌ Not found!"}[lang])
    
    await wait.delete()

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    print("Bot polling boshlandi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
