from telethon import TelegramClient, events
import asyncio

# ====== AYARLAR ======
api_id = 35819402
api_hash = "61cfbb3a501c02a69f2458a250de8c97"
session = "1BJWap1sBu2GB-W-NfsLgKn-LwBvY1Ve4Gu8tfjjOoaS0URegxfb1Kzoq9vgI_CsbTJHeMgdXiOJ_u9ft0enVvkBcfVduysUb1NTfam4BDAR-6jr98LHnWoPtqLA_vmt3I6YZ6rpn4P6m3QAsIuc8X2_H7vZji7vHXaPSRnq3ay1EELuSZ3C5tOqKs-NpQyNyG6Jlybk6pXztQniCzT9GCqgk7wOGXbD8tjG4Ouh7aAkqVo2boHO0kF_IYLk29ymwew__xshPmVIhM7qwiNtv7HeB8bKh-ElsrXII9G6r10toc9Wy7W2fdd_E1m3ixBpS70diZ0R2s4JlNLJygs01CQPOtwjVKoc="

# =====================

bot = TelegramClient(session, api_id, api_hash)

spam_tasks = {}

# ===== /commands =====
@bot.on(events.NewMessage(pattern="/commands"))
async def commands(event):
    text = """
komutlar:

/spam <adet> <mesaj>
belirtilen mesajı hızlı spamlar

/loop <mesaj>
sürekli mesaj gönderir

/stop
aktif spamı durdurur

/ping
bot çalışıyor mu bakarsın
"""
    await event.reply(text)

# ===== ping =====
@bot.on(events.NewMessage(pattern="/ping"))
async def ping(event):
    await event.reply("aktif")

# ===== spam =====
@bot.on(events.NewMessage(pattern="/spam"))
async def spam(event):
    args = event.message.text.split(maxsplit=2)

    if len(args) < 3:
        return await event.reply("kullanım: /spam adet mesaj")

    count = int(args[1])
    msg = args[2]

    for i in range(count):
        await event.respond(msg)

# ===== loop spam =====
@bot.on(events.NewMessage(pattern="/loop"))
async def loop(event):
    msg = event.message.text.split(" ",1)[1]
    chat = event.chat_id

    async def spam_loop():
        while True:
            await bot.send_message(chat, msg)
            await asyncio.sleep(0.2)

    spam_tasks[chat] = asyncio.create_task(spam_loop())
    await event.reply("loop başladı")

# ===== stop =====
@bot.on(events.NewMessage(pattern="/stop"))
async def stop(event):
    chat = event.chat_id

    if chat in spam_tasks:
        spam_tasks[chat].cancel()
        del spam_tasks[chat]
        await event.reply("loop durduruldu")

# ===== start =====
bot.start()
print("userbot aktif")
bot.run_until_disconnected()