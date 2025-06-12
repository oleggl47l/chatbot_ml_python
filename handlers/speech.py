import logging
import os
import tempfile

import speech_recognition as sr
from pydub import AudioSegment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    ffmpeg_path = r"D:\ffmpeg-2025-06-08-git-5fea5e3e11-full_build\ffmpeg-2025-06-08-git-5fea5e3e11-full_build\bin\ffmpeg.exe"
    if os.path.exists(ffmpeg_path):
        os.environ["PATH"] = os.path.dirname(ffmpeg_path) + os.pathsep + os.environ["PATH"]
        os.environ["PYDUB_FFMPEG"] = ffmpeg_path
        logger.info(f"FFmpeg добавлен в PATH и PYDUB_FFMPEG: {ffmpeg_path}")
    else:
        logger.warning(f"FFmpeg не найден по пути: {ffmpeg_path}")
except Exception as e:
    logger.error(f"Ошибка при настройке ffmpeg: {e}")




class SpeechHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.max_file_size = 20 * 1024 * 1024  # 20MB
        self.supported_languages = {
            'ru-RU': 'Русский',
            'en-US': 'English'
        }

    async def handle_voice(self, update, context):
        """Обрабатывает голосовые сообщения и аудио файлы"""
        try:
            if update.message.voice:
                file = await context.bot.get_file(update.message.voice.file_id)
            elif update.message.audio:
                file = await context.bot.get_file(update.message.audio.file_id)
            else:
                return "Ошибка: Неизвестный тип аудио сообщения"

            if file.file_size > self.max_file_size:
                return f"Ошибка: Файл слишком большой (максимум {self.max_file_size/1024/1024}MB)"

            file_path = os.path.join(tempfile.gettempdir(), f"{file.file_id}.ogg")
            await file.download_to_drive(file_path)

            wav_path = os.path.join(tempfile.gettempdir(), f"{file.file_id}.wav")
            audio = AudioSegment.from_ogg(file_path)
            audio.export(wav_path, format="wav")

            with sr.AudioFile(wav_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data, language='ru-RU')

            os.remove(file_path)
            os.remove(wav_path)

            return text

        except sr.UnknownValueError:
            return "Ошибка: Не удалось распознать речь"
        except sr.RequestError as e:
            logger.error(f"Ошибка сервиса распознавания речи: {e}")
            return "Ошибка: Проблема с сервисом распознавания речи"
        except Exception as e:
            logger.error(f"Ошибка при обработке голосового сообщения: {e}")
            return f"Ошибка: {str(e)}" 