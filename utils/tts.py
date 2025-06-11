import os
import uuid
import subprocess
from gtts import gTTS

AUDIO_DIR = "temp_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

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
