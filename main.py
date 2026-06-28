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
# TOKENS
# =====================================================================
TOKEN = "8936913831:AAE29TdwOI_aRKdIM2I2Njn71ma3umAWHbY"
# =====================================================================

dp = Dispatcher()
USER_LANG_FILE = "user_langs.json"

def load_user_langs():
    if os.path.exists(USER_LANG_FILE):
        with open(USER_LANG_FILE, "r") as f:
            return json.load(f)
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
        'btn_lang': "🌐 TILNI O'ZGARTIRISH",
        'caption': "🎶 {title}\n\n📥 @Mucis_Saved_bot",
        'searching': "⌛ Qidirilmoqda...",
        'not_found': "❌ Qo'shiq topilmadi!",
        'error': "⚠️ Xatolik!"
    },
    'ru': {
        'welcome': "MUSIC SAVE 🎧\n\nВведите название песни или исполнителя:",
        'btn_settings': "⚙️ НАСТРОЙКИ",
        'btn_info': "ℹ️ О БОТЕ",
        'btn_lang': "🌐 ИЗМЕНИТЬ ЯЗЫК",
        'caption': "🎶 {title}\n\n📥 @Mucis_Saved_bot",
        'searching': "⌛ Поиск...",
        'not_found': "❌ Песня не найдена!",
        'error': "⚠️ Ошибка!"
    }
}

def clean_title(title: str) -> str:
    title = re.sub(r'(?i)(\[.*?\]|\(.*?\))', '', title)
    title = re.sub(r'(?i)(official audio|official video|lyric video|hd|mp3|audio|video|clip|klip)', '', title)
    title = title.replace('_', ' ').replace('-', ' - ')
    title = re.sub(r'\s+', ' ', title).strip()
    return title

async def download_track(search_text: str):
    # Ingliz tilidagi musiqani izlash uchun "English song" qo'shamiz
    query_for_search = f"{search_text} English song"
    cleaned_text = re.sub(r'[^\w\s\-]', '', query_for_search).strip()
    
    strategies = [
        {"source": f"scsearch1:{cleaned_text} track", "type": "SoundCloud"},
        {"source": f"ytsearch1:{cleaned_text} official audio", "type": "YouTube"}
    ]

    loop = asyncio.get_event_loop()
    for strategy in strategies:
        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "quiet": True,
            "writethumbnail": True,
            "http_headers": {"User-Agent": "Mozilla/5.0"}
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await loop.run_in_executor(None, lambda: ydl.extract_info(strategy["source"], download=True))
                if info and 'entries' in info and len(info['entries']) > 0:
                    entry = info["entries"][0]
                    file_path = f"downloads/{entry['id']}.{entry.get('ext', 'mp3')}"
                    raw_title = entry.get("title", search_text)
                    clean_name = clean_title(raw_title)
                    performer = entry.get("uploader", "Music Save")

                    thumb_path = None
                    thumbnail_url = entry.get("thumbnail")
                    if thumbnail_url:
                        temp_thumb = f"downloads/{entry['id']}.jpg"
                        try:
                            urllib.request.urlretrieve(thumbnail_url, temp_thumb)
                            if os.path.exists(temp_thumb): thumb_path = temp_thumb
                        except: pass

                    if os.path.exists(file_path):
                        return {"file_path": file_path, "title": clean_name, "performer": performer, "thumb_path": thumb_path}
        except Exception as e: 
            print(f"Yuklashda xato: {e}")
            continue
    return None

def get_main_keyboard(lang):
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=TEXTS[lang]['btn_settings']), KeyboardButton(text=TEXTS[lang]['btn_info'])]], resize_keyboard=True)

def get_lang_keyboard():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский")]], resize_keyboard=True)

@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    user_id = str(message.from_user.id)
    user_langs = load_user_langs()
    if user_id in user_langs:
        lang = user_langs[user_id]
        await message.answer(TEXTS[lang]['welcome'], reply_markup=get_main_keyboard(lang))
    else:
        await message.answer("🤖 Tilni tanlang / Выберите язык:", reply_markup=get_lang_keyboard())

@dp.message(F.text.in_(["🇺🇿 O'zbekcha", "🇷🇺 Русский"]))
async def set_language(message: Message):
    lang = 'uz' if "O'zbekcha" in message.text else 'ru'
    save_user_lang(message.from_user.id, lang)
    await message.answer(TEXTS[lang]['welcome'], reply_markup=get_main_keyboard(lang))

@dp.message(F.text)
async def handle_music_search(message: Message):
    user_id = str(message.from_user.id)
    user_langs = load_user_langs()
    if user_id not in user_langs:
        await cmd_start(message)
        return
    lang = user_langs[user_id]
    
    if message.text in [TEXTS[lang]['btn_settings'], TEXTS[lang]['btn_lang']]:
        await message.answer("🌐 Tilni tanlang:", reply_markup=get_lang_keyboard())
        return
    if message.text == TEXTS[lang]['btn_info']:
        await message.answer(TEXTS[lang]['welcome'], reply_markup=get_main_keyboard(lang))
        return

    wait_msg = await message.answer(TEXTS[lang]['searching'])
    track = await download_track(message.text)
    
    if track:
        caption = TEXTS[lang]['caption'].format(title=track['title'])
        audio_file = FSInputFile(track['file_path'])
        thumb_file = FSInputFile(track['thumb_path']) if track['thumb_path'] else None
        
        await message.answer_audio(audio=audio_file, caption=caption, title=track['title'], performer=track['performer'], thumbnail=thumb_file)
        
        if os.path.exists(track['file_path']): os.remove(track['file_path'])
        if track['thumb_path'] and os.path.exists(track['thumb_path']): os.remove(track['thumb_path'])
    else:
        await message.answer(TEXTS[lang]['not_found'])
    await wait_msg.delete()

async def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
