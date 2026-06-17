import asyncio
import os
import re
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import yt_dlp

TOKEN = "8936913831:AAHlOjfRzV4gyA6Goki50D_NLN3OIlC8FbQ"
dp = Dispatcher()
user_data = {}

TEXTS = {
    'uz': {
        'welcome': "👋 *Salom! InstaTubeBot-ga xush kelibsiz!*\n\n📥 Instagram, YouTube yoki TikTok havolasini yuboring, men uni yuklab beraman!",
        'btn_video_mode': "📥 VIDEO YUKLASH",
        'btn_lang': "🌐 TILNI O'ZGARTIRISH",
        'prompt_video': "👇 Havolani yuboring:",
        'error': "⚠️ Yuklashda xatolik. Havola to'g'riligini tekshiring.",
        'remind': "💡 Iltimos, video havolasini yuboring!"
    },
    'ru': {
        'welcome': "👋 *Привет! Добро пожаловать в InstaTubeBot!*\n\n📥 Отправьте ссылку (Instagram, YouTube, TikTok), и я скачаю видео!",
        'btn_video_mode': "📥 СКАЧАТЬ ВИДЕО",
        'btn_lang': "🌐 СМЕНИТЬ ЯЗЫК",
        'prompt_video': "👇 Отправьте ссылку:",
        'error': "⚠️ Ошибка при загрузке.",
        'remind': "💡 Пожалуйста, отправьте ссылку на видео!"
    },
    'en': {
        'welcome': "👋 *Hello! Welcome to InstaTubeBot!*\n\n📥 Send an Instagram, YouTube, or TikTok link, and I will download it!",
        'btn_video_mode': "📥 DOWNLOAD VIDEO",
        'btn_lang': "🌐 CHANGE LANGUAGE",
        'prompt_video': "👇 Send the link:",
        'error': "⚠️ An error occurred. Check the link.",
        'remind': "💡 Please, send a video link!"
    }
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

async def download_video(url: str):
    ydl_opts = {"format": "best[ext=mp4]/best", "outtmpl": "downloads/vid_%(id)s.%(ext)s", "quiet": True, "http_headers": HEADERS}
    loop = asyncio.get_event_loop()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            return {"file_path": f"downloads/vid_{info['id']}.{info.get('ext', 'mp4')}", "title": info.get("title", "Video"), "id": info['id']} if info else None
    except: return None

async def download_audio_from_url(url: str):
    ydl_opts = {"format": "bestaudio/best", "outtmpl": "downloads/aud_%(id)s.%(ext)s", "quiet": True, "http_headers": HEADERS}
    loop = asyncio.get_event_loop()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            return {"file_path": f"downloads/aud_{info['id']}.{info.get('ext', 'mp3')}", "title": info.get("title", "Audio")} if info else None
    except: return None

def get_main_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=TEXTS[lang]['btn_video_mode'])], [KeyboardButton(text=TEXTS[lang]['btn_lang'])]], resize_keyboard=True)

def get_lang_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇬🇧 English")]], resize_keyboard=True)

@dp.callback_query(F.data.startswith("getmp3_"))
async def process_callback_mp3(callback_query: CallbackQuery):
    await callback_query.answer("🎵 Yuklanmoqda...")
    video_id = callback_query.data.split("_")[1]
    track_info = await download_audio_from_url(f"https://www.youtube.com/watch?v={video_id}")
    if track_info:
        await callback_query.message.reply_audio(audio=FSInputFile(track_info['file_path']), title=track_info['title'])
        os.remove(track_info['file_path'])
    else: await callback_query.message.reply("⚠️ Xatolik yuz berdi.")

@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.reply("🤖 *Tilni tanlang / Выберите язык / Select language:*", reply_markup=get_lang_keyboard(), parse_mode=ParseMode.MARKDOWN)

@dp.message(F.text)
async def handle_message(message: Message):
    chat_id = message.chat.id
    if chat_id not in user_data: user_data[chat_id] = {'lang': 'uz'}
    
    text = message.text
    if text in ["🇺🇿 O'zbekcha", "🇷🇺 Русский", "🇬🇧 English"]:
        lang = 'uz' if text == "🇺🇿 O'zbekcha" else ('ru' if text == "🇷🇺 Русский" else 'en')
        user_data[chat_id]['lang'] = lang
        await message.reply(TEXTS[lang]['welcome'], reply_markup=get_main_keyboard(lang), parse_mode=ParseMode.MARKDOWN)
        return

    lang = user_data[chat_id].get('lang', 'uz')
    if "http" in text:
        wait_msg = await message.reply("⏳ *Yuklanmoqda...*")
        info = await download_video(text)
        if info:
            kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🎵 MP3", callback_data=f"getmp3_{info['id']}")]])
            await message.reply_video(video=FSInputFile(info['file_path']), caption=f"📹 *{info['title']}*", reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
            os.remove(info['file_path'])
            await wait_msg.delete()
        else: await wait_msg.edit_text(TEXTS[lang]['error'])
    elif text in [TEXTS[l]['btn_video_mode'] for l in TEXTS]:
        await message.reply(TEXTS[lang]['prompt_video'])
    else: await message.reply(TEXTS[lang]['remind'])

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
