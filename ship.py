import asyncio
from telethon import TelegramClient, events

api_id = 35819402
api_hash = "61cfbb3a501c02a69f2458a250de8c97"
session = "1BJWap1sBu2GB-W-NfsLgKn-LwBvY1Ve4Gu8tfjjOoaS0URegxfb1Kzoq9vgI_CsbTJHeMgdXiOJ_u9ft0enVvkBcfVduysUb1NTfam4BDAR-6jr98LHnWoPtqLA_vmt3I6YZ6rpn4P6m3QAsIuc8X2_H7vZji7vHXaPSRnq3ay1EELuSZ3C5tOqKs-NpQyNyG6Jlybk6pXztQniCzT9GCqgk7wOGXbD8tjG4Ouh7aAkqVo2boHO0kF_IYLk29ymwew__xshPmVIhM7qwiNtv7HeB8bKh-ElsrXII9G6r10toc9Wy7W2fdd_E1m3ixBpS70diZ0R2s4JlNLJygs01CQPOtwjVKoc="

OWNER = 6534222591
admins = [OWNER]
afk_users = {}

bot = TelegramClient(session, api_id, api_hash)


def is_admin(user):
    return user in admins


# ===== commands =====
@bot.on(events.NewMessage(pattern="/commands"))
async def commands(event):
    if not is_admin(event.sender_id):
        return

    text = """
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
"""
    await event.reply(text)


# ===== admin ekle =====
@bot.on(events.NewMessage(pattern="/addadmin"))
async def addadmin(event):
    if event.sender_id != OWNER:
        return

    if not event.is_reply:
        return await event.reply("birine yanıt ver")

    user = await event.get_reply_message()
    uid = user.sender_id

    admins.append(uid)

    await event.reply("admin eklendi")


# ===== admin sil =====
@bot.on(events.NewMessage(pattern="/deladmin"))
async def deladmin(event):
    if event.sender_id != OWNER:
        return

    if not event.is_reply:
        return await event.reply("birine yanıt ver")

    user = await event.get_reply_message()
    uid = user.sender_id

    if uid in admins:
        admins.remove(uid)

    await event.reply("admin silindi")


# ===== spam =====
@bot.on(events.NewMessage(pattern="/spam"))
async def spam(event):
    if not is_admin(event.sender_id):
        return

    args = event.text.split(maxsplit=2)

    count = int(args[1])
    msg = args[2]

    for i in range(count):
        await event.respond(msg)


# ===== loop =====
loops = {}

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


@bot.on(events.NewMessage(pattern="/stop"))
async def stop(event):
    if not is_admin(event.sender_id):
        return

    chat = event.chat_id

    if chat in loops:
        loops[chat].cancel()
        del loops[chat]

        await event.reply("loop durdu")


# ===== mention =====
@bot.on(events.NewMessage(pattern="/mention"))
async def mention(event):
    if not is_admin(event.sender_id):
        return

    args = event.text.split(maxsplit=2)

    msg = args[1]
    count = int(args[2])

    reply = await event.get_reply_message()
    user = await reply.get_sender()

    mention = f"[{user.first_name}](tg://user?id={user.id})"

    for i in range(count):
        await event.respond(f"{mention} {msg}",parse_mode="md")


# ===== reply raid =====
@bot.on(events.NewMessage(pattern="/reply"))
async def reply(event):
    if not is_admin(event.sender_id):
        return

    args = event.text.split(maxsplit=2)

    msg = args[1]
    count = int(args[2])

    reply = await event.get_reply_message()

    for i in range(count):
        await event.respond(msg,reply_to=reply.id)


# ===== raid =====
@bot.on(events.NewMessage(pattern="/raid"))
async def raid(event):
    if not is_admin(event.sender_id):
        return

    args = event.text.split(maxsplit=2)

    msg = args[1]
    count = int(args[2])

    reply = await event.get_reply_message()
    user = await reply.get_sender()

    mention = f"[{user.first_name}](tg://user?id={user.id})"

    for i in range(count):
        await event.respond(f"{mention} {msg}",reply_to=reply.id,parse_mode="md")


# ===== tagall =====
@bot.on(events.NewMessage(pattern="/tagall"))
async def tagall(event):
    if not is_admin(event.sender_id):
        return

    msg = event.text.split(" ",1)[1]

    users = await bot.get_participants(event.chat_id)

    text = msg + "\n"

    for u in users:
        text += f"[{u.first_name}](tg://user?id={u.id}) "

    await event.respond(text,parse_mode="md")


# ===== purge =====
@bot.on(events.NewMessage(pattern="/purge"))
async def purge(event):
    if not is_admin(event.sender_id):
        return

    args = event.text.split()

    count = int(args[1])

    async for msg in bot.iter_messages(event.chat_id,limit=count):
        await msg.delete()


# ===== userinfo =====
@bot.on(events.NewMessage(pattern="/userinfo"))
async def userinfo(event):
    if not is_admin(event.sender_id):
        return

    if not event.is_reply:
        return await event.reply("birine yanıt ver")

    user = await event.get_reply_message()
    sender = await user.get_sender()

    text=f"""
isim: {sender.first_name}
id: {sender.id}
username: @{sender.username}
"""

    await event.reply(text)


# ===== afk =====
@bot.on(events.NewMessage(pattern="/afk"))
async def afk(event):
    reason = event.text.split(" ",1)[1]
    afk_users[event.sender_id] = reason
    await event.reply("afk oldun")


@bot.on(events.NewMessage)
async def afk_reply(event):
    if event.sender_id in afk_users:
        del afk_users[event.sender_id]

    if event.is_reply:
        user = await event.get_reply_message()
        uid = user.sender_id

        if uid in afk_users:
            await event.reply(f"afk: {afk_users[uid]}")


print("userbot aktif")
bot.start()
bot.run_until_disconnected()