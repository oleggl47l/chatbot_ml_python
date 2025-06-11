import os
import uuid
import subprocess
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from gtts import gTTS
from io import BytesIO

AUDIO_DIR = "temp_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)
tts_cache = {}


def text_to_speech_ogg(text: str) -> str:
    """Создает голосовой файл в формате OGG (opus), возвращает путь к файлу"""
    uid = uuid.uuid4().hex
    mp3_path = os.path.join(AUDIO_DIR, f"{uid}.mp3")
    ogg_path = os.path.join(AUDIO_DIR, f"{uid}.ogg")

    tts = gTTS(text, lang="ru")
    tts.save(mp3_path)

    subprocess.run([
        "ffmpeg", "-y", "-i", mp3_path,
        "-c:a", "libopus", "-b:a", "64k",
        ogg_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    os.remove(mp3_path)
    return ogg_path


def get_tts_keyboard(self: str) -> InlineKeyboardMarkup:
    short_id = str(uuid.uuid4())[:8]
    tts_cache[short_id] = self
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🔊 Прочитать", callback_data=f"tts|{short_id}")
    ]])


async def tts_callback(self: Update, context: ContextTypes.DEFAULT_TYPE):
    query = self.callback_query
    await query.answer()
    data = query.data

    if not data.startswith("tts|"):
        return

    short_id = data.split("|", 1)[1]
    text = tts_cache.get(short_id)

    if not text:
        await query.message.reply_text("Текст для озвучки не найден или устарел.")
        return

    tts = gTTS(text=text[:500], lang='ru')
    voice = BytesIO()
    tts.write_to_fp(voice)
    voice.seek(0)

    await query.message.reply_voice(voice)
