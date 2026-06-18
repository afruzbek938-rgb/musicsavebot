import asyncio
import os
import json
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton
import yt_dlp

TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQ"
ADMIN_ID = 6949980794  # Sizning IDingiz
USER_DATA_FILE = "users.json"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- BAZA ---
def load_data():
    if not os.path.exists(USER_DATA_FILE): return {}
    with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return {}

def save_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# --- MENYULAR ---
def main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🎵 Musiqa yuklash")],
        [KeyboardButton(text="💎 Mening limitim"), KeyboardButton(text="🔗 Taklif qilish")]
    ], resize_keyboard=True)

def admin_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📊 Statistika")],
        [KeyboardButton(text="⬅️ Asosiy menyuga qaytish")]
    ], resize_keyboard=True)

# --- BUYRUQLAR ---
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    users = load_data()
    uid = str(message.from_user.id)
    if uid not in users:
        users[uid] = {"limit": 50}
        save_data(users)
    await message.answer(f"Assalomu alaykum, <b>{message.from_user.first_name}</b>!", reply_markup=main_menu())

@dp.message(F.text == "/admin")
async def admin_cmd(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🛠 Admin panelga xush kelibsiz!", reply_markup=admin_menu())
    else:
        await message.answer("❌ Siz admin emassiz!")

@dp.message(F.text == "📊 Statistika")
async def show_stats(message: Message):
    if message.from_user.id == ADMIN_ID:
        users = load_data()
        await message.answer(f"👥 Jami foydalanuvchilar: {len(users)} ta")

@dp.message(F.text == "⬅️ Asosiy menyuga qaytish")
async def back_to_main(message: Message):
    await message.answer("Asosiy menyuga qaytdingiz.", reply_markup=main_menu())

# --- QOLGAN QISMLAR (Limit, Referal va Yuklash avvalgidek qoladi) ---
# ... (Musiqa yuklash funksiyasini shu yerga joylang) ...

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
