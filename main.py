import asyncio
import os
import json
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.filters import Command
import yt_dlp

# Token
TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQ"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Ishga tushirish funksiyasi
async def main():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    print("Bot muvaffaqiyatli ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
