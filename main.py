import asyncio
import os
import re
import json
import urllib.request
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
import yt_dlp

# =====================================================================
TOKEN = "8936913831:AAE29TdwOI_aRKdIM2I2Njn71ma3umAWHbY"
# =====================================================================

dp = Dispatcher()
USER_LANG_FILE = "user_langs.json"

def load_user_langs():
    if os.path.exists(USER_LANG_FILE):
        with open(USER_LANG_FILE, "r") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_user_lang(user_id, lang):
    user_langs = load_user_langs()
    user_langs[str(user_id)] = lang
    with open(USER_LANG_FILE, "w") as f:
        json.dump(user_langs, f)

TEXTS = {
    'uz': {
        'welcome': "MUSIC SAVE 🎧\n\nQo'shiq nomi yoki ijrochisini yozing:",
        'btn_settings': "⚙️ SOZLAMALAR",
        'btn_info': "ℹ️ BOT HAQIDA",
        'caption': "🎶 {title}\n\n📥 @Mucis_Saved_bot",
        'searching': "⌛ Qidirilmoqda...",
        'not_found': "❌ Qo'shiq topilmadi!",
        'error': "⚠️ Xatolik!"
    },
    'ru': {
        'welcome': "MUSIC SAVE 🎧\n\nВведите название песни или исполнителя:",
        'btn_settings': "⚙️ НАСТРОЙКИ",
        'btn_info': "ℹ️ О БОТЕ",
        'caption': "🎶 {title}\n\n📥 @Mucis_Saved_bot",
        'searching': "⌛ Поиск...",
        'not_found': "❌ Песня не найдена!",
        'error': "⚠️ Ошибка!"
    }
}

def clean_title(title: str) -> str:
    title = re.sub(r'(?i)(\[.*?\]|\(.*?\))', '', title)
    title = re.sub(r'(?i)(official audio|official video|lyric video|hd|mp3|audio|video|clip|klip)', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title

async def download_track(search_text: str):
    # Inglizcha musiqa uchun so'rovni boyitamiz
    query = f"{search_text} English song"
    strategies = [f"scsearch1:{query}", f"ytsearch1:{query}"]
    
    loop = asyncio.get_running_loop()
    
    for source in strategies:
        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "quiet": True,
            "writethumbnail": True
        }
        
        try:
            def run():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(source, download=True)
            
            info = await loop.run_in_executor(None, run)
            if 'entries' in info and info['entries']:
                entry = info['entries'][0]
                file_path = f"downloads/{entry['id']}.{entry.get('ext', 'mp3')}"
                
                # Fayl kengaytmasi muammosini hal qilish
                if not os.path.exists(file_path):
                    for ext in ['webm', 'm4a', 'mp3']:
                        path = f"downloads/{entry['id']}.{ext}"
                        if os.path.exists(path):
                            file_path = path
                            break
                
                thumb_path = None
                if entry.get('thumbnail'):
                    thumb_path = f"downloads/{entry['id']}.jpg"
                    urllib.request.urlretrieve(entry['thumbnail'], thumb_path)
                
                return {"file": file_path, "title": clean_title(entry['title']), "thumb": thumb_path}
        except: continue
    return None

@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer("🇺🇿 Tilni tanlang / 🇷🇺 Выберите язык:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский")]], resize_keyboard=True))

@dp.message(F.text.in_(["🇺🇿 O'zbekcha", "🇷🇺 Русский"]))
async def set_lang(message: Message):
    lang = 'uz' if "O'zbekcha" in message.text else 'ru'
    save_user_lang(message.from_user.id, lang)
    await message.answer(TEXTS[lang]['welcome'], reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TEXTS[lang]['btn_settings']), KeyboardButton(text=TEXTS[lang]['btn_info'])]], resize_keyboard=True))

@dp.message(F.text)
async def search_handler(message: Message):
    lang = load_user_langs().get(str(message.from_user.id), 'uz')
    wait = await message.answer(TEXTS[lang]['searching'])
    track = await download_track(message.text)
    
    if track:
        await message.answer_audio(audio=FSInputFile(track['file']), 
                                   caption=TEXTS[lang]['caption'].format(title=track['title']),
                                   thumbnail=FSInputFile(track['thumb']) if track['thumb'] else None)
        try:
            os.remove(track['file'])
            if track['thumb']: os.remove(track['thumb'])
        except: pass
    else:
        await message.answer(TEXTS[lang]['not_found'])
    await wait.delete()

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
