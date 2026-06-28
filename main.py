import asyncio
import os
import re
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
import yt_dlp

# =====================================================================
TOKEN = "8615110980:AAHl1YLkvZ1Z8qUr45uI3dMwx-lR0lKVp1E"
VERSION = "1.12.2"
# =====================================================================

dp = Dispatcher()
user_language = {} # Foydalanuvchi tilini saqlash uchun lug'at

TEXTS = {
    'uz': {
        'welcome': "👋 Salom, **{name}**! InstaTubeBot-ga xush kelibsiz!",
        'btn_video_mode': "📥 VIDEO YUKLASH",
        'btn_lang': "🌐 TILNI O'ZGARTIRISH",
        'prompt_video': "👇 Iltimos, video havolasini yuboring (Instagram, YouTube, TikTok, Facebook, Likee...):",
        'error': "⚠️ Xatolik! Havolani tekshiring yoki video yopiq profilda bo'lishi mumkin.",
        'remind': "💡 Iltimos, menga video havolasini yuboring!"
    },
    'ru': {
        'welcome': "👋 Привет, **{name}**! Добро пожаловать в InstaTubeBot!",
        'btn_video_mode': "📥 СКАЧАТЬ ВИДЕО",
        'btn_lang': "🌐 СМЕНИТЬ ЯЗЫК",
        'prompt_video': "👇 Пожалуйста, отправьте ссылку на видео (Instagram, YouTube, TikTok, Facebook, Likee...):",
        'error': "⚠️ Ошибка! Проверьте ссылку или настройки приватности.",
        'remind': "💡 Пожалуйста, отправьте ссылку на видео!"
    },
    'en': {
        'welcome': "👋 Hello, **{name}**! Welcome to InstaTubeBot!",
        'btn_video_mode': "📥 DOWNLOAD VIDEO",
        'btn_lang': "🌐 CHANGE LANGUAGE",
        'prompt_video': "👇 Please send the video link (Instagram, YouTube, TikTok, Facebook, Likee...):",
        'error': "⚠️ Error! Please check the link or privacy settings.",
        'remind': "💡 Please send a video link!"
    }
}

# --- YUKLASH FUNKSIYASI ---
async def download_media(url: str):
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "quiet": True,
        "nocheckcertificate": True,
    }
    loop = asyncio.get_event_loop()
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            return info
    except Exception as e:
        print(f"ERROR: {e}")
        return None

# --- KLAVIATURALAR ---
def get_main_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=TEXTS[lang]['btn_video_mode'])],
            [KeyboardButton(text=TEXTS[lang]['btn_lang'])]
        ],
        resize_keyboard=True
    )

def get_lang_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇺🇸 English")]], 
        resize_keyboard=True
    )

# --- HANDLERLAR ---
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    user_name = message.from_user.first_name
    if message.chat.id in user_language:
        lang = user_language[message.chat.id]
        await message.answer(TEXTS[lang]['welcome'].format(name=user_name), 
                             reply_markup=get_main_keyboard(lang), parse_mode=ParseMode.MARKDOWN)
    else:
        await message.answer(f"👋 Salom/Привет/Hello, **{user_name}**!\n🌍 Tilni tanlang:", reply_markup=get_lang_keyboard(), parse_mode=ParseMode.MARKDOWN)

@dp.message(F.text.in_(["🇺🇿 O'zbekcha", "🇷🇺 Русский", "🇺🇸 English"]))
async def set_lang(message: Message):
    lang_map = {"🇺🇿 O'zbekcha": 'uz', "🇷🇺 Русский": 'ru', "🇺🇸 English": 'en'}
    selected_lang = lang_map[message.text]
    user_language[message.chat.id] = selected_lang
    user_name = message.from_user.first_name
    await message.answer(TEXTS[selected_lang]['welcome'].format(name=user_name), 
                         reply_markup=get_main_keyboard(selected_lang), parse_mode=ParseMode.MARKDOWN)

@dp.message(F.text)
async def handle_message(message: Message):
    chat_id = message.chat.id
    lang = user_language.get(chat_id, 'uz')
    text = message.text

    if text in [TEXTS['uz']['btn_video_mode'], TEXTS['ru']['btn_video_mode'], TEXTS['en']['btn_video_mode']]:
        await message.answer(TEXTS[lang]['prompt_video'])
        return
    
    if text in ["🌐 TILNI O'ZGARTIRISH", "🌐 СМЕНИТЬ ЯЗЫК", "🌐 CHANGE LANGUAGE"]:
        await message.answer("🌍 Tilni tanlang:", reply_markup=get_lang_keyboard())
        return

    url_match = re.search(r'(https?://[^\s]+)', text)
    if url_match:
        url = url_match.group(1)
        wait_msg = await message.reply("⏳ *Yuklanmoqda...*", parse_mode=ParseMode.MARKDOWN)
        
        info = await download_media(url)
        
        if info:
            file_path = f"downloads/{info['id']}.{info['ext']}"
            caption = f"📹 *{info.get('title', 'Video')}*\n\n🤖 Bot versiyasi: {VERSION}"
            
            await message.reply_video(video=FSInputFile(file_path), caption=caption, parse_mode=ParseMode.MARKDOWN)
            os.remove(file_path)
            await wait_msg.delete()
        else:
            await wait_msg.edit_text(TEXTS[lang]['error'])
    else:
        await message.answer(TEXTS[lang]['remind'])

async def main() -> None:
    if not os.path.exists('downloads'): os.makedirs('downloads')
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
