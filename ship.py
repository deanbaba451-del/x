from pyrogram import Client, filters
from PIL import Image, ImageDraw, ImageFont
import hashlib
from datetime import date

API_ID = 30150271
API_HASH = "bbe0e183c97ead8a86926ecb95938486"
BOT_TOKEN = "8511414999:AAEx249ogF9gKy6dWNJTb1gDSlcIHw-XgxE"

app = Client("shipbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


def circle(pfp):
    img = Image.open(pfp).resize((300,300)).convert("RGBA")

    mask = Image.new("L",(300,300),0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0,0,300,300),fill=255)

    img.putalpha(mask)
    return img


def ship_percent(id1,id2):
    today = str(date.today())
    seed = f"{id1}{id2}{today}"
    h = hashlib.md5(seed.encode()).hexdigest()
    return int(h,16)%101


@app.on_message(filters.command("ship"))
async def ship(client,message):

    if len(message.command) >= 3:
        user1 = await client.get_users(message.command[1])
        user2 = await client.get_users(message.command[2])

    elif message.reply_to_message:
        user1 = message.from_user
        user2 = message.reply_to_message.from_user

    elif len(message.command) == 2:
        user1 = message.from_user
        user2 = await client.get_users(message.command[1])

    else:
        return await message.reply("Kullanım: /ship @user1 @user2")

    p1 = await client.download_media(
        (await client.get_chat_photos(user1.id,limit=1)).__anext__()
    )

    p2 = await client.download_media(
        (await client.get_chat_photos(user2.id,limit=1)).__anext__()
    )

    img1 = circle(p1)
    img2 = circle(p2)

    percent = ship_percent(user1.id,user2.id)

    bg = Image.new("RGBA",(800,400),(255,240,245))

    bg.paste(img1,(100,50),img1)
    bg.paste(img2,(400,50),img2)

    draw = ImageDraw.Draw(bg)

    draw.text((360,170),"❤️",fill=(255,0,0))

    draw.text((340,320),f"%{percent}",fill=(255,0,0))

    bg.save("ship.png")

    await message.reply_photo(
        "ship.png",
        caption=f"{user1.first_name} ❤️ {user2.first_name}\nUyumluluk: %{percent}"
    )


app.run()