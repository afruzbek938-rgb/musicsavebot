import asyncio
import os
import json
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.filters import Command
import yt_dlp

TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQ"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Foydalanuvchi tilini saqlash
LANG_FILE = "user_langs.json"
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
    await message.answer("Tilni tanlang / Выберите язык / Select language:", reply_markup=get_lang_kb())

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    user_langs[str(callback.from_user.id)] = lang
    with open(LANG_FILE, "w") as f: json.dump(user_langs, f)
    
    msg = {"uz": "Til o'zgartirildi! Qo'shiq nomini yozing:", 
           "ru": "Язык изменен! Напишите название песни:", 
           "en": "Language changed! Send song name:"}
    await callback.message.edit_text(msg[lang])

@dp.message(F.text)
async def handle_music(message: Message):
    lang = user_langs.get(str(message.from_user.id), "en")
    wait = await message.answer("⏳ ...")
    
    ydl_opts = {
        "format": "bestaudio/best",
        "default_search": "ytsearch1:",
        "outtmpl": "downloads/%(title)s.%(ext)s", # Fayl nomi qo'shiq nomi bo'ladi
        "quiet": True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(message.text, download=True)
            entry = info["entries"][0]
            file_name = f"{entry['title']}.{entry.get('ext', 'mp3')}"
            
            # Bot atmetkasi bilan yuborish
            await message.answer_audio(
                audio=FSInputFile(f"downloads/{file_name}"), 
                caption=f"🎼 {entry['title']}\n\n🤖 @Music_Save_Bot"
            )
            os.remove(f"downloads/{file_name}")
    except:
        await message.answer({"uz": "❌ Topilmadi!", "ru": "❌ Не найдено!", "en": "❌ Not found!"}[lang])
    await wait.delete()

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
