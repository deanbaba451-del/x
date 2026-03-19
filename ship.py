import os
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- RENDER İÇİN FLASK ---
app = Flask('')
@app.route('/')
def home(): return "Guard System Online!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- AYARLAR ---
OWNER_ID = 6534222591
BOT_TOKEN = "8681886836:AAGuYsx7B5OZLZ68vTQoR8OAi7DWk61aXZA"
status = {"is_active": True}
# Yetkileri takip etmek için (Geçici hafıza)
temp_perms = {}

def get_kb(u_id, c_id):
    # Hafızadan yetkileri al, yoksa varsayılan yap
    key = f"{u_id}_{c_id}"
    p = temp_perms.get(key, {
        "info": False, "ban": True, "del": True, "inv": True, 
        "pin": True, "story": False, "vc": False, "top": False, "tag": False, "add": False, "anon": False
    })
    
    def t(k): return "✅" if p[k] else "❌"
    def l(k): return "✅" if p[k] else "🔒" # Bazıları görselde kilitliydi

    keyboard = [
        [InlineKeyboardButton(f"{t('info')} Grup bilgilerini değiştir", callback_data=f"tog_info_{key}")],
        [InlineKeyboardButton(f"{t('ban')} Kullanıcıları banla", callback_data=f"tog_ban_{key}"), 
         InlineKeyboardButton(f"{t('del')} Mesajları sil", callback_data=f"tog_del_{key}")],
        [InlineKeyboardButton(f"{t('inv')} Üye ekle", callback_data=f"tog_inv_{key}"), 
         InlineKeyboardButton(f"{t('pin')} Sabit mesajlar", callback_data=f"tog_pin_{key}")],
        [InlineKeyboardButton(f"{t('story')} Hikayeler yayınla", callback_data=f"tog_story_{key}")],
        [InlineKeyboardButton(f"{l('vc')} Sesli aramayı yönet", callback_data=f"tog_vc_{key}")],
        [InlineKeyboardButton(f"{l('top')} Konuları yönet", callback_data=f"tog_top_{key}")],
        [InlineKeyboardButton(f"❌ Edit member tags", callback_data=f"tog_tag_{key}")],
        [InlineKeyboardButton(f"❌ Yeni admin ekle", callback_data=f"tog_add_{key}")],
        [InlineKeyboardButton(f"🔒 Anonim Admin", callback_data=f"tog_anon_{key}")],
        [InlineKeyboardButton("Kaydet ✔️", callback_data=f"save_{key}")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data.startswith("tog_"):
        _, p_type, key = data.split("_", 2)
        u_id, c_id = key.split("_")
        
        # Yetkiyi tersine çevir (Trueysa False, Falseysa True)
        temp_perms[key][p_type] = not temp_perms[key][p_type]
        
        # Klavyeyi güncelle (Görsel olarak ✅/❌ değişir)
        await query.edit_message_reply_markup(reply_markup=get_kb(u_id, c_id))
        
        # GRUPTA YETKİYİ ANLIK GÜNCELLE
        p = temp_perms[key]
        try:
            await context.bot.promote_chat_member(
                chat_id=int(c_id), user_id=int(u_id),
                can_change_info=p["info"], can_restrict_members=p["ban"],
                can_delete_messages=p["del"], can_invite_users=p["inv"],
                can_pin_messages=p["pin"], can_manage_video_chats=p["vc"],
                can_manage_topics=p["top"]
            )
        except: pass # Botun yetkisi yetmezse sadece görsel değişir

    elif data.startswith("save_"):
        await query.answer("Yetkiler başarıyla uygulandı!", show_alert=True)

async def command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    uid, cid, text = update.effective_user.id, update.effective_chat.id, update.message.text.lower()

    if uid == OWNER_ID:
        if text == ".bon": status["is_active"] = True; return await update.message.reply_text("online")
        if text == ".boff": status["is_active"] = False; return await update.message.reply_text("offline")

    if text.startswith(",admin") or text.startswith(".admin"):
        target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
        if not target: return
        
        # Hafızayı hazırla
        key = f"{target.id}_{cid}"
        temp_perms[key] = {"info": False, "ban": True, "del": True, "inv": True, "pin": True, "story": False, "vc": False, "top": False, "tag": False, "add": False, "anon": False}
        
        # Gruba mesaj at
        await update.message.reply_text(f"guard\n@{target.username} [{target.id}]\n👮 Admin yapılmıştır.\n• Tag: x")
        
        # Sahibe DM at
        _, kb = "🕹 İzinler", get_kb(target.id, cid)
        await context.bot.send_message(chat_id=uid, text=f"🕹 **İzinler**\n👤 @{target.username}\n👥 {update.effective_chat.title}", reply_markup=kb, parse_mode=ParseMode.MARKDOWN)

async def guard_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if status["is_active"] and update.message.new_chat_members:
        for m in update.message.new_chat_members:
            if m.is_bot:
                adder = update.effective_user
                await update.message.reply_text(f"[{adder.first_name}](tg://user?id={adder.id}) insecure fucks your mother.", parse_mode=ParseMode.MARKDOWN)
                try:
                    await context.bot.ban_chat_member(update.effective_chat.id, m.id)
                    await context.bot.ban_chat_member(update.effective_chat.id, adder.id)
                except: pass

def main():
    Thread(target=run).start()
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, command_handler))
    app_bot.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, guard_bot))
    app_bot.add_handler(CallbackQueryHandler(callback_handler))
    app_bot.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__": main()
