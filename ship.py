import os
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- FLASK (Render 7/24) ---
app = Flask('')
@app.route('/')
def home(): return "Guard Online!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- AYARLAR ---
OWNER_ID = 6534222591
BOT_TOKEN = "TOKEN_BURAYA"
status = {"is_active": True}

# --- TÜM BUTONLARIN OLDUĞU PANEL ---
def get_full_admin_panel(user_id, user_name, chat_title):
    keyboard = [
        [InlineKeyboardButton("❌ Grup bilgilerini değiştir", callback_data=f"p_info_{user_id}")],
        [InlineKeyboardButton("✅ Kullanıcıları banla", callback_data=f"p_ban_{user_id}"), 
         InlineKeyboardButton("✅ Mesajları sil", callback_data=f"p_del_{user_id}")],
        [InlineKeyboardButton("✅ Üye ekle", callback_data=f"p_inv_{user_id}"), 
         InlineKeyboardButton("✅ Sabit mesajlar", callback_data=f"p_pin_{user_id}")],
        [InlineKeyboardButton("❌ Hikayeler yayınla", callback_data=f"p_st1_{user_id}")],
        [InlineKeyboardButton("❌ Hikayeleri düze...", callback_data=f"p_st2_{user_id}"),
         InlineKeyboardButton("❌ Hikayeleri sil", callback_data=f"p_st3_{user_id}")],
        [InlineKeyboardButton("🔒 Sesli aramayı yönet", callback_data=f"p_vc_{user_id}")],
        [InlineKeyboardButton("🔒 Konuları yönet", callback_data=f"p_top_{user_id}")],
        [InlineKeyboardButton("❌ Edit member tags", callback_data=f"p_tag_{user_id}")],
        [InlineKeyboardButton("❌ Yeni admin ekle", callback_data=f"p_add_{user_id}")],
        [InlineKeyboardButton("🔒 Anonim Admin", callback_data=f"p_anon_{user_id}")],
        [InlineKeyboardButton("Kaydet ✔️", callback_data="save")]
    ]
    text = f"🕹 **İzinler**\n👤 {user_name} [{user_id}]\n👥 {chat_title}"
    return text, InlineKeyboardMarkup(keyboard)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # Butonun dönmesini durdurur
    if query.data == "save":
        await query.edit_message_text("✅ Yetkiler başarıyla kaydedildi ve uygulandı.")

async def handle_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip().lower()

    # .bon / .boff
    if user_id == OWNER_ID:
        if text == ".bon":
            status["is_active"] = True
            return await update.message.reply_text("online")
        if text == ".boff":
            status["is_active"] = False
            return await update.message.reply_text("offline")

    # ,admin
    if text.startswith(",admin"):
        target_user = None
        if update.message.reply_to_message:
            target_user = update.message.reply_to_message.from_user
        else:
            args = text.split()
            if len(args) > 1 and args[1].isdigit():
                try: target_user = await context.bot.get_chat(int(args[1]))
                except: pass
        
        if not target_user: return

        try:
            # Grupta Admin Yap
            await context.bot.promote_chat_member(
                chat_id=chat_id, user_id=target_user.id,
                can_manage_chat=True, can_delete_messages=True, can_restrict_members=True,
                can_invite_users=True, can_pin_messages=True, can_manage_video_chats=True
            )
            
            # Grup Onay Mesajı
            msg_text = f"guard\n@{target_user.username} [{target_user.id}]\n👮 Admin yapılmıştır.\n• Tag: x"
            btn = InlineKeyboardMarkup([[InlineKeyboardButton("🕹 İzinler ↗️", callback_data=f"open_dm_{target_user.id}")]])
            await update.message.reply_text(msg_text, reply_markup=btn)

            # DM'den Full Panel Gönder
            panel_text, panel_kb = get_full_admin_panel(target_user.id, f"@{target_user.username}", update.effective_chat.title)
            await context.bot.send_message(chat_id=user_id, text=panel_text, reply_markup=panel_kb, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            await update.message.reply_text(f"Hata: {e}")

async def guard_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not status["is_active"]: return
    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            if member.is_bot:
                adder = update.effective_user
                try:
                    await update.message.reply_text(f"[{adder.first_name}](tg://user?id={adder.id}) insecure fucks your mother.", parse_mode=ParseMode.MARKDOWN)
                    await context.bot.ban_chat_member(update.effective_chat.id, member.id)
                    await context.bot.ban_chat_member(update.effective_chat.id, adder.id)
                except: pass

def main():
    Thread(target=run).start()
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_commands))
    app_bot.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, guard_logic))
    app_bot.add_handler(CallbackQueryHandler(button_callback))
    app_bot.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__": main()
