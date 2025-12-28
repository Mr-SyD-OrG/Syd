import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from helper.database import db

START_TEXT = (
    "**ꜱᴇɴᴅ ᴍᴇ ꜰɪʟᴇꜱ** ᴏʀ **ᴀᴅᴅ ᴍᴇ ᴛᴏ ᴀ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ** ᴡʜᴇʀᴇ ꜰɪʟᴇꜱ ᴀʀᴇ ᴘʀᴇꜱᴇɴᴛ — "
    "ɪ’ʟʟ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴀᴅᴅ ɴᴇᴡ ꜰɪʟᴇꜱ ʀᴇᴄɪᴇᴠᴇᴅ ɪɴ ᴛʜᴏꜱᴇ ᴄʜᴀᴛ ɪɴᴛᴏ **[ᴏᴜʀ ʙᴏᴛꜱ](https://t.me/Bot_Cracker/17)**.\n\n"
    "ᴜꜱᴇ /save ᴛᴏ ᴀᴅᴅ ᴇxɪꜱᴛɪɴɢ ꜰɪʟᴇꜱ ɪɴᴛᴏ ᴏᴜʀ ᴅʙ"
    "🌱 **ᴜᴩᴅᴀᴛᴇꜱ ¹:** @Mod_Moviez_X 🧩\n"
    "🌱 **ᴜᴘᴅᴀᴛᴇꜱ ²:** @Bot_Cracker 🧩\n\n"
)

button = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🌱 Jᴏɪɴ Oᴜʀ Uᴩᴅᴀᴛᴇꜱ Cʜᴀɴɴᴇʟ 🌱", url="https://t.me/Bot_Cracker")
    ],[
        InlineKeyboardButton("Sᴜᴩᴩᴏʀᴛ", url="https://t.me/+O1mwQijo79s2MjJl"),
        InlineKeyboardButton("Oᴡɴᴇʀ", user_id=1733124290)
    ],[
        InlineKeyboardButton("🧩 Oᴜʀ Bᴏᴛꜱ 🧩", url="https://t.me/Bot_Cracker/17")
    ]
])


@Client.on_message(filters.command("start"))
async def start(client, message):
    user = message.from_user
    await db.add_user(client, message)
    await message.reply_text(
        START_TEXT,
        reply_markup=button,
        disable_web_page_preview=True
    )
        
@Client.on_message(filters.command("forward", prefixes="/"))
async def forward_messages(client, message):
    try:
        # /forward from_chat to_chat start_id end_id pause_seconds
        parts = message.text.split()
        if len(parts) < 5:
            return await message.reply(
                "Usage: `/forward {from} {to} {start_id} {end_id} {pause_seconds}`",
                quote=True
            )

        from_chat = parts[1]
        to_chat = parts[2]
        start_id = int(parts[3])
        end_id = int(parts[4])
        pause_seconds = float(parts[5]) if len(parts) > 5 else 1.0

        sent_count = 0
        total_messages = end_id - start_id + 1
        progress_msg = await message.reply("Forwarding started...")

        for msg_id in range(start_id, end_id + 1):
            try:
                msg = await client.get_messages(from_chat, msg_id)
                if not msg:
                    continue

                while True:
                    try:
                        await msg.copy(to_chat)
                        sent_count += 1
                        break
                    except FloodWait as e:
                        print(f"FloodWait: Sleeping {e.value} seconds for message {msg_id}")
                        await asyncio.sleep(e.value)
                    except Exception as e:
                        print(f"Failed to copy message {msg_id}: {e}")
                        break

                if sent_count % 100 == 0:
                    try:
                        await progress_msg.edit_text(
                            f"📤 Forwarded {sent_count}/{total_messages} (`{sent_count + start_id}`) messages..."
                        )
                    except Exception as e:
                        print(f"Progress edit failed: {e}")
                await asyncio.sleep(pause_seconds)

            except Exception as e:
                print(f"Error fetching message {msg_id}: {e}")

        await progress_msg.edit_text("✅ Forwarding completed.")

    except Exception as e:
        await message.reply(f"❌ Error: {e}")


ADULT_WORDS = {
    "porn", "xxx", "sex", "nude", "naked", "adult", "18+",
    "blowjob", "hardcore", "hentai", "nsfw", "boobs",
    "pussy", "dick", "cock", "asshole", "XVideos"
}

import re

VID_PATTERN = re.compile(r"^VID_[A-Za-z0-9]{5,}", re.IGNORECASE)
ONLY_NUM = re.compile(r"^\d+$")

def has_adult_content(text: str) -> bool:
    if not text:
        return False
    text = text.replace("_", " ").lower()
    return any(w in text for w in ADULT_WORDS)
    


send_lock = asyncio.Semaphore(3)
async def safe_send(client, **kwargs):
    async with send_lock:
        while True:
            try:
                await asyncio.sleep(1.8)
                return await client.send_cached_media(**kwargs)
            except FloodWait as e:
                await asyncio.sleep(e.value + 1)


MIN_SIZE = 70 * 1024 * 1024  # 70 MB
VERIFIED_USERS = [1733124290]

@Client.on_message(filters.document | filters.video | filters.audio)
async def auto_forward(client, message):
    if message.from_user and message.from_user.id not in VERIFIED_USERS: return await message.reply("❌ You are not verified. Message @Syd_Xyz 🌿") and await client.send_message(1733124290, f"🚨 Unverified user\n👤 {message.from_user.mention}\n🆔 `{message.from_user.id}`")
    media = getattr(message, message.media.value, None)
    if not media or (media.file_size or 0) < MIN_SIZE:
        return  # ignore files < 70MB

    fn = getattr(media, "file_name", "") or ""
    t = f"{fn} {msg.caption or ''}".lower()
    if ONLY_NUM.match(fn): return
    r = "VID_Xxxxx pattern" if VID_PATTERN.match(fn) else "Adult keyword detected" if any(w in t for w in ADULT_WORDS) else None
    if r: await client.send_message(ADMIN_ID, f"🚫 **Blocked File**\n📛 {r}\n📁 `{fn or 'No name'}`\n🆔 `{chat_id}` | 🧾 `{msg.id}`"); return
    
    await safe_send(
        client,
        chat_id=-1002518698743,
        file_id=media.file_id,
        caption = f"{message.caption or ''}\n Chat ID: `{message.chat.id}`"
    )


@Client.on_chat_member_updated(filters.chat_type.channel)
async def bot_added_channel(client, update):
    if update.new_chat_member and update.new_chat_member.user.is_self:
        chat = update.chat

        text = (
            "➕ **Bot Added to Channel**\n\n"
            f"📛 Name: {chat.title}\n"
            f"🆔 ID: `{chat.id}`\n"
            f"👥 Members: `{chat.members_count or 'Unknown'}`\n"
            f"🧾 Last Msg ID: `{update.new_chat_member.date}`\n"
            f"📢 Type: Channel"
        )

        await client.send_message(1733124290, text)


@Client.on_message(filters.new_chat_members)
async def bot_added_group(client, message):
    me = await client.get_me()

    for m in message.new_chat_members:
        if m.id == me.id:
            chat = message.chat
            adder = message.from_user

            text = (
                "➕ **Bot Added to Group**\n\n"
                f"📛 Name: {chat.title}\n"
                f"🆔 ID: `{chat.id}`\n"
                f"👥 Members: `{chat.members_count}`\n"
                f"🧾 Last Msg ID: `{message.id}`\n"
                f"➕ Added by: {adder.mention if adder else 'Unknown'}\n"
                f"👥 Type: {chat.type}"
            )

            await client.send_message(1733124290, text)


@Client.on_message(filters.command("save") & (filters.group | filters.channel))
async def save_history(client, message):
    chat_id = message.chat.id
    end_id = message.id  # command message ID

    await message.reply(f"📥 Saving messages **1 → {end_id}**")

    async for msg in client.iter_messages(chat_id, min_id=0, max_id=end_id):
        if not msg.media:
            continue

        media = getattr(msg, msg.media.value, None)
        if not media:
            continue

        if (media.file_size or 0) < MIN_SIZE:
            return

        fn = getattr(media, "file_name", "") or ""
        if ONLY_NUM.match(fn): return
        t = f"{fn} {msg.caption or ''}".lower()
        r = "VID_Xxxxx pattern" if VID_PATTERN.match(fn) else "Adult keyword detected" if any(w in t for w in ADULT_WORDS) else None
        if r: await client.send_message(ADMIN_ID, f"🚫 **Blocked File**\n📛 {r}\n📁 `{fn or 'No name'}`\n🆔 `{chat_id}` | 🧾 `{msg.id}`"); return
    

        caption = (
            f"{msg.caption or ''}\n\n"
            f"🆔 Chat ID: `{chat_id}`\n"
            f"🧾 Msg ID: `{msg.id}`"
        )

        await safe_send(
            client,
            chat_id=-1003137700522,
            file_id=media.file_id,
            caption=caption
        )
        
