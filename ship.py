import logging
import asyncio
from datetime import datetime
import pytz
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Ayarlar
TOKEN = "8676544410:AAFc0R4T6t1rLs2r53kqfXd4adA8iOY1dEY"
LOG_ID = 6534222591
TR = pytz.timezone('Europe/Istanbul')

# Durumlar
SONG, ARTIST, PHOTO = range(3)

# Render için basit HTTP Sunucusu
app = Flask('')
@app.route('/')
def home(): return "Bot Aktif."

def run(): app.run(host='0.0.0.0', port=8080)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Lütfen mp3 dosyasını gönderin.")
    return SONG

async def get_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['audio'] = update.message.audio.file_id
    await update.message.reply_text("Şarkı ismi nedir?.")
    return ARTIST

async def get_artist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Sanatçı ismi nedir?.")
    return PHOTO

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['artist'] = update.message.text
    await update.message.reply_text("Yeni kapak fotoğrafını gönderin.")
    return PHOTO

async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1].file_id
    user = update.message.from_user
    time_str = datetime.now(TR).strftime('%H:%M:%S')
    
    # Kullanıcı etiketi
    mention = f"@{user.username}" if user.username else f"[{user.first_name}](tg://user?id={user.id})"
    
    # Kullanıcıya gönder
    await update.message.reply_photo(photo, caption=f"{context.user_data['artist']} - {context.user_data['name']}.")
    await update.message.reply_audio(context.user_data['audio'], title=context.user_data['name'], performer=context.user_data['artist'])

    # Log Gönder (Eğer yapan kişi Log ID değilse)
    if user.id != LOG_ID:
        log_text = f"Yeni İşlem!\nKullanıcı: {mention}\nSaat: {time_str}."
        await context.bot.send_message(LOG_ID, log_text, parse_mode='Markdown')
        await context.bot.send_audio(LOG_ID, context.user_data['audio'], caption="Eski hali.")
        await context.bot.send_photo(LOG_ID, photo, caption=f"Yeni hali: {context.user_data['artist']} - {context.user_data['name']}.")

    await update.message.reply_text("İşlem tamamlandı.")
    return ConversationHandler.END

def main():
    Thread(target=run).start()
    app_tg = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SONG: [MessageHandler(filters.AUDIO, get_song)],
            ARTIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_artist)],
            PHOTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_photo), 
                    MessageHandler(filters.PHOTO, finish)],
        },
        fallbacks=[]
    )

    app_tg.add_handler(conv_handler)
    app_tg.run_polling()

if __name__ == '__main__':
    main()
