import logging, asyncio, pytz
from datetime import datetime
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Ayarlar
TOKEN = "8676544410:AAHiCQiN3bf3AhvYMnC5arsNeU2cNIavj2k"
LOG_ID = 6534222591
TR = pytz.timezone('Europe/Istanbul')
SONG, NAME, ARTIST, PHOTO = range(4)

app = Flask('')
@app.route('/')
def home(): return "OK"
def run(): app.run(host='0.0.0.0', port=8080)

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await u.message.reply_text("mp3 at.")
    return SONG

async def get_song(u: Update, c: ContextTypes.DEFAULT_TYPE):
    c.user_data['audio'] = u.message.audio.file_id
    await u.message.reply_text("isim?.")
    return NAME

async def get_name(u: Update, c: ContextTypes.DEFAULT_TYPE):
    c.user_data['name'] = u.message.text
    await u.message.reply_text("sanatçı?.")
    return ARTIST

async def get_artist(u: Update, c: ContextTypes.DEFAULT_TYPE):
    c.user_data['artist'] = u.message.text
    await u.message.reply_text("pp at.")
    return PHOTO

async def finish(u: Update, c: ContextTypes.DEFAULT_TYPE):
    photo = u.message.photo[-1].file_id
    user = u.message.from_user
    time = datetime.now(TR).strftime('%H:%M')
    tag = f"@{user.username}" if user.username else f"[{user.first_name}](tg://user?id={user.id})"
    
    # Kullanıcıya
    await u.message.reply_photo(photo, caption=f"{c.user_data['artist']} - {c.user_data['name']}.")
    await u.message.reply_audio(c.user_data['audio'], title=c.user_data['name'], performer=c.user_data['artist'])

    # Log (Owner değilse)
    if user.id != LOG_ID:
        log_txt = f"işlem: {tag}\nsaat: {time}."
        await c.bot.send_message(LOG_ID, log_txt, parse_mode='Markdown')
        await c.bot.send_photo(LOG_ID, photo, caption=f"yeni: {c.user_data['artist']} - {c.user_data['name']}.")

    await u.message.reply_text("tamam.")
    return ConversationHandler.END

def main():
    Thread(target=run).start()
    bot = Application.builder().token(TOKEN).build()
    
    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SONG: [MessageHandler(filters.AUDIO, get_song)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ARTIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_artist)],
            PHOTO: [MessageHandler(filters.PHOTO, finish)],
        },
        fallbacks=[]
    )
    bot.add_handler(conv)
    bot.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
