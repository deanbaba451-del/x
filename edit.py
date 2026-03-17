import os
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from flask import Flask
from threading import Thread

web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot aktif."

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

API_ID = 20275001
API_HASH = "26e474f4a17fe5b306cc6ecfd2a1ed55"
BOT_TOKEN = "8579539233:AAGX9Dd0hTGV2_yhBbyzr7n7xbBMym7152Y"
SESSION_STRING = "BAE1XzkAQODlnE7Q5p49txSKPSdxVCdBv4ZnzUE1TGF9OGngoeZSgUoNg9AXyPbRMgmDsQ0hoyv9fVy8JnEu0SUs6DkcQ5i6GqNlQnfXM3pbMr4JNx8KilGKWgUcoU8FQm5EiWRQVTL-1xXGx1TxkoR_UYXeycIqvL4uVwvDSAVRaRCbwKgafBL49WPXoWq0HVpP46YBlT0ocjTeHIOUBKtnoAGQMQL079ok91BSbMOH0GXritBykHeCispbLyzRNt4KmSpLZlEKzkxlicYTvdDaPOzvmZRnnIUoASoi2YSCwe4Le0sR0YZ-P_5GvN-vm8CdmWa947-_ZSVxuCvGSXniz8yeFQAAAAHfRBiOAA"

if SESSION_STRING:
    app = Client(
        "guard_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION_STRING
    )
else:
    app = Client(
        "guard_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN
    )

CHAT_SETTINGS = {}
message_store = {}

def get_content_fingerprint(message: Message):
    text = message.text or message.caption or ""
    media_id = "none"
    
    media_attrs = ["photo", "video", "sticker", "animation", "voice", "video_note", "audio", "document"]
    for attr in media_attrs:
        media = getattr(message, attr, None)
        if media:
            media_id = getattr(media, "file_unique_id", "none")
            break
            
    return f"{text}_{media_id}"

@app.on_message(filters.command(["editon", "editoff"]) & filters.group)
async def toggle_guard(client: Client, message: Message):
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status != enums.ChatMemberStatus.OWNER:
            return 

        is_on = (message.command[0] == "editon")
        CHAT_SETTINGS[message.chat.id] = is_on
        
        durum = "AKTIF" if is_on else "DEAKTIF"
        msg = await message.reply(f" online {durum}")
        
        await message.delete()
        await asyncio.sleep(3)
        await msg.delete()
    except Exception as e:
        print(f"Yetki hatasi: {e}")

@app.on_message(filters.group & ~filters.command(["editon", "editoff"]), group=1)
async def track_messages(client: Client, message: Message):
    message_store[message.id] = get_content_fingerprint(message)
    
    if len(message_store) > 3000:
        oldest_key = next(iter(message_store))
        message_store.pop(oldest_key)

@app.on_edited_message(filters.group)
async def handle_edits(client: Client, message: Message):
    if not CHAT_SETTINGS.get(message.chat.id, True):
        return
        
    if message.from_user and message.from_user.is_bot:
        return

    if message.location:
        return

    original = message_store.get(message.id)
    current = get_content_fingerprint(message)

    if original and original == current:
        return
    
    protected_words = ["PLATE:", "ADMIN:", "UPDATE:", "STATUS:"]
    content_upper = (message.text or message.caption or "").upper()
    if any(word in content_upper for word in protected_words):
        return

    try:
        user_mention = message.from_user.mention if message.from_user else "Kullanıcı"
        
        await message.delete()
        
        warning = await client.send_message(
            message.chat.id, 
            f" {user_mention}, bu grupta mesaj düzenlemek yasaktır. mesajın silindi!"
        )
        
        message_store.pop(message.id, None)
        await asyncio.sleep(5)
        await warning.delete()
    except Exception as e:
        print(f"Islem hatasi: {e}")

if __name__ == "__main__":
    print("kurşun adres sormaz ki")
    Thread(target=run_web, daemon=True).start()
    app.run()