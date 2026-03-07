from telethon import TelegramClient, events

api_id = 35819402
api_hash = "61cfbb3a501c02a69f2458a250de8c97"
session = "1BJWap1sBu2GB-W-NfsLgKn-LwBvY1Ve4Gu8tfjjOoaS0URegxfb1Kzoq9vgI_CsbTJHeMgdXiOJ_u9ft0enVvkBcfVduysUb1NTfam4BDAR-6jr98LHnWoPtqLA_vmt3I6YZ6rpn4P6m3QAsIuc8X2_H7vZji7vHXaPSRnq3ay1EELuSZ3C5tOqKs-NpQyNyG6Jlybk6pXztQniCzT9GCqgk7wOGXbD8tjG4Ouh7aAkqVo2boHO0kF_IYLk29ymwew__xshPmVIhM7qwiNtv7HeB8bKh-ElsrXII9G6r10toc9Wy7W2fdd_E1m3ixBpS70diZ0R2s4JlNLJygs01CQPOtwjVKoc="

OWNER = 6534222591

bot = TelegramClient(session, api_id, api_hash)

@bot.on(events.NewMessage(pattern="/raid"))
async def raid(event):

    if event.sender_id != OWNER:
        return

    if not event.is_reply:
        return await event.reply("bir mesaja yanıt ver")

    args = event.text.split(maxsplit=2)

    if len(args) < 3:
        return await event.reply("kullanım: /raid mesaj sayı")

    msg = args[1]
    count = int(args[2])

    reply = await event.get_reply_message()
    user = await reply.get_sender()

    mention = f"[{user.first_name}](tg://user?id={user.id})"

    for _ in range(count):
        await event.respond(f"{mention} {msg}", reply_to=reply.id, parse_mode="md")

print("raid userbot aktif")
bot.start()
bot.run_until_disconnected()bot.run_until_disconnected()