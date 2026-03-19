import os
import logging
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- LOG AYARLARI ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- FLASK SUNUCUSU (Render 7/24 İçin) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Online!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- AYARLAR ---
OWNER_ID = 6534222591  # Senin ID'n
BOT_TOKEN = "TOKEN_BURAYA" # BotFather'dan aldığın token
status = {"is_active": True} # Başlangıçta online

# --- YETKİ VERME FONKSİYONU ---
async def handle_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip().lower()

    # 1. .bon / .boff (Sadece Sahibi)
    if user_id == OWNER_ID:
        if text == ".bon":
            status["is_active"] = True
            return await update.message.reply_text("online")
        if text == ".boff":
            status["is_active"] = False
            return await update.message.reply_text("offline")

    # 2. ,admin / ,unadmin (Reply veya ID ile)
    if text.startswith(",admin") or text.startswith(",unadmin"):
        target_id = None
        
        # Yanıtla (Reply) ile kullanım
        if update.message.reply_to_message:
            target_id = update.message.reply_to_message.from_user.id
        # ID ile kullanım (,admin 123456)
        else:
            args = text.split()
            if len(args) > 1 and args[1].isdigit():
                target_id = int(args[1])

        if not target_id:
            return await update.message.reply_text("❌ Kullanım: Birini yanıtlayın veya ID yazın: `,admin 123456`")

        try:
            if ",admin" in text:
                # GERÇEK YETKİ VERME
                await context.bot.promote_chat_member(
                    chat_id=chat_id, user_id=target_id,
                    can_manage_chat=True, can_delete_messages=True,
                    can_restrict_members=True, can_invite_users=True, can_pin_messages=True
                )
                
                # GÖRSELDEKİ BUTONLAR
                keyboard = [
                    [InlineKeyboardButton("❌ Grup bilgilerini değiştir", callback_data='n')],
                    [InlineKeyboardButton("✅ Kullanıcıları banla", callback_data='n'), 
                     InlineKeyboardButton("✅ Mesajları sil", callback_data='n')],
                    [InlineKeyboardButton("✅ Üye ekle", callback_data='n'), 
                     InlineKeyboardButton("✅ Sabit mesajlar", callback_data='n')],
                    [InlineKeyboardButton("❌ Hikayeler yayınla", callback_data='n')],
                    [InlineKeyboardButton("Kaydet ✔️", callback_data='n')]
                ]
                await update.message.reply_text(
                    f"👮 **Admin yapılmıştır.**\n\n🕹 **İzinler**\n👤 ID: `{target_id}`\n• Tag: x",
                    reply_markup=InlineKeyboardMarkup(keyboard), 
                    parse_mode=ParseMode.MARKDOWN
                )
            elif ",unadmin" in text:
                await context.bot.promote_chat_member(chat_id=chat_id, user_id=target_id, can_manage_chat=False)
                await update.message.reply_text(f"❌ {target_id} yetkileri çekildi.")

        except Exception as e:
            await update.message.reply_text(f"Hata: {e}\n(Botun 'Yönetici Ekleme' yetkisi açık mı?)")

# --- KORUMA MANTIĞI (BOT EKLEME) ---
async def guard_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not status["is_active"]:
        return

    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            if member.is_bot:
                adder = update.effective_user
                mention = f"[{adder.first_name}](tg://user?id={adder.id})"
                
                # İstediğin mesaj
                await update.message.reply_text(f"{mention} insecure fucks your mother.", parse_mode=ParseMode.MARKDOWN)
                
                try:
                    # Botu ve Ekleyeni Banla
                    await context.bot.ban_chat_member(update.effective_chat.id, member.id)
                    await context.bot.ban_chat_member(update.effective_chat.id, adder.id)
                except:
                    pass

def main():
    # Flask'ı arka planda başlat
    keep_alive()
    
    # Botu başlat
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handlerlar
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_commands))
    application.add
