/import asyncio
from telethon import TelegramClient, events

api_id = 35819402
api_hash = "61cfbb3a501c02a69f2458a250de8c97"
session = "1BJWap1sBu2GB-W-NfsLgKn-LwBvY1Ve4Gu8tfjjOoaS0URegxfb1Kzoq9vgI_CsbTJHeMgdXiOJ_u9ft0enVvkBcfVduysUb1NTfam4BDAR-6jr98LHnWoPtqLA_vmt3I6YZ6rpn4P6m3QAsIuc8X2_H7vZji7vHXaPSRnq3ay1EELuSZ3C5tOqKs-NpQyNyG6Jlybk6pXztQniCzT9GCqgk7wOGXbD8tjG4Ouh7aAkqVo2boHO0kF_IYLk29ymwew__xshPmVIhM7qwiNtv7HeB8bKh-ElsrXII9G6r10toc9Wy7W2fdd_E1m3ixBpS70diZ0R2s4JlNLJygs01CQPOtwjVKoc="

bot = TelegramClient(session, api_id, api_hash)

# ===== VERİ =====
data = {
    "owner": 6534222591,
    "admins": [6534222591],
    "afk": {}
}

loops = {}

# ===== admin kontrol =====
def is_admin(user):
    return user in data["admins"]

# ===== commands =====
@bot.on(events.NewMessage(pattern="/commands"))
async def commands(event):
    if not is_admin(event.sender_id):
        return

    await event.reply("""
komutlar

/spam sayı mesaj
/loop mesaj
/stop
/mention mesaj sayı
/reply mesaj sayı
/raid mesaj sayı
/tagall mesaj
/purge sayı
/userinfo
/afk sebep
/addadmin
/deladmin
""")

# ===== admin ekle =====
@bot.on(events.NewMessage(pattern="/addadmin"))
async def addadmin(event):

    if event.sender_id != data["owner"]:
        return

    if not event.is_reply:
        return await event.reply("bir mesaja yanıt ver")

    reply = await event.get_reply_message()
    uid = reply.sender_id

    if uid not in data["admins"]:
        data["admins"].append(uid)

    await event.reply("admin eklendi")

# ===== admin sil =====
@bot.on(events.NewMessage(pattern="/deladmin"))
async def deladmin(event):

    if event.sender_id != data["owner"]:
        return

    if not event.is_reply:
        return await event.reply("bir mesaja yanıt ver")

    reply = await event.get_reply_message()
    uid = reply.sender_id

    if uid in data["admins"]:
        data["admins"].remove(uid)

    await event.reply("admin silindi")

# ===== spam =====
@bot.on(events.NewMessage(pattern="/spam"))
async def spam(event):

    if not is_admin(event.sender_id):
        return

    args = event.text.split(maxsplit=2)

    count = int(args[1])
    msg = args[2]

    for _ in range(count):
        await event.respond(msg)

# ===== loop =====
@bot.on(events.NewMessage(pattern="/loop"))
async def loop(event):

    if not is_admin(event.sender_id):
        return

    msg = event.text.split(" ",1)[1]
    chat = event.chat_id

    async def spam_loop():
        while True:
            await bot.send_message(chat,msg)
            await asyncio.sleep(0.4)

    loops[chat] = asyncio.create_task(spam_loop())
    await event.reply("loop başladı")

# ===== stop =====
@bot.on(events.NewMessage(pattern="/stop"))
async def stop(event):

    if not is_admin(event.sender_id):
        return

    chat = event.chat_id

    if chat in loops:
        loops[chat].cancel()
        del loops[chat]

        await event.reply("loop durdu")

# ===== afk =====
@bot.on(events.NewMessage(pattern="/afk"))
async def afk(event):

    if not is_admin(event.sender_id):
        return

    reason = event.text.split(" ",1)[1]
    data["afk"][event.sender_id] = reason

    await event.reply("afk oldun")

# ===== afk cevap =====
@bot.on(events.NewMessage)
async def afk_reply(event):

    if event.is_reply:
        reply = await event.get_reply_message()
        uid = reply.sender_id

        if uid in data["afk"]:
            await event.reply(f"afk: {data['afk'][uid]}")

print("userbot aktif")
bot.start()
bot.run_until_disconnected()