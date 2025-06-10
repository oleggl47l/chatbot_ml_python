import logging
from telegram import Update
from telegram.ext import ContextTypes

from handlers.speech import SpeechHandler

logger = logging.getLogger(__name__)

class VoiceHandler:
    def __init__(self, speech_handler: SpeechHandler):
        self.speech_handler = speech_handler

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает голосовые сообщения"""
        processing_message = await update.message.reply_text("Обрабатываю голосовое сообщение...")
        
        text = await self.speech_handler.handle_voice(update, context)
        
        if text.startswith("Ошибка"):
            await processing_message.edit_text(text)
            return
            
        await processing_message.delete()
        
        await update.message.reply_text(f"Распознано: {text}")
        
        return text 