import asyncio
import os
import json
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.filters import Command
import yt_dlp

TOKEN = "8936913831:AAE29TdwOI_aRKdIM2I2Njn71ma3umAWHbY"
bot = Bot(token=TOKEN)
dp = Dispatcher()

LANG_FILE = "user_langs.json"

# Tilni faylga saqlash
def save_langs(langs):
    with open(LANG_FILE, "w") as f:
        json.dump(langs, f)

# Fayldan yuklab olish
def load_langs():
    if os.path.exists(LANG_FILE):
        with open(LANG_FILE, "r") as f:
            return json.load(f)
    return {}

user_langs = load_langs()

# (Tugmalar va boshqa qismlar avvalgidek qoladi...)

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    user_langs[str(callback.from_user.id)] = lang
    save_langs(user_langs) # Har safar o'zgarganda saqlaymiz
    text = {"uz": "Til o'zgartirildi!", "ru": "Язык изменен!", "en": "Language changed!"}
    await callback.message.edit_text(text[lang], reply_markup=get_main_kb(lang))

# handle_music funksiyasida esa shunday o'zgartiramiz:
@dp.message(F.text)
async def handle_music(message: Message):
    # Har doim fayldan oladi, shuning uchun eslab qoladi
    lang = user_langs.get(str(message.from_user.id), "en") 
    # ... qolgan kod qismi o'zgarishsiz ...
