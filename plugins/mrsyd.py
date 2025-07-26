from pyrogram import Client, filters
import asyncio
from pyrogram.types import Message



FORWARD_TO = 1733124290  # replace with your user ID

# List of allowed chat IDs
ALLOWED_CHAT_IDS = [-1001605140211, -1002287422608, -1002601575630, -1001823125512]  # add your other chat IDs here

@Client.on_message(filters.group & filters.text & filters.incoming)
async def delilter(client, message: Message):
    if message.chat.id not in ALLOWED_CHAT_IDS:
        return

    text = message.text.lower()
    words = text.split()

    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in ("administrator", "creator"):
            return
    except Exception as e:
        # If we can't get member info (e.g. user left), skip to be safe
        pass
        
    # Check for disallowed links or mentions
    for word in words:
        if word.startswith("http") or (word.startswith("@") and word != "@admin"):
            await message.delete()
            await client.send_message(FORWARD_TO, "Deleted")
            return

    # Check for @admin and forward if found
    if "@admin" in text:
        await client.forward_messages(chat_id=FORWARD_TO, from_chat_id=message.chat.id, message_ids=message.id)
        await client.send_message(FORWARD_TO, f"#AdminTagged from {message.from_user.mention if message.from_user else 'unknown'}")
   
    
    if message.chat.id != -1001605140211:
        return
    await asyncio.sleep(40)
    await message.delete()


from pyrogram import Client, filters
from pyrogram.types import Message
import re

CHANNEL_ID = -1001234567890  # replace with your target channel ID

@Client.on_message(filters.command("addbot") & filters.private)
async def add_new_bot(client, message: Message):
    async def ask(prompt):
        await message.reply(prompt + "\n\n(Use /cancel to stop)", quote=True)
        response = await client.ask(message.chat.id, timeout=120)
        if response.text.lower() == "/cancel":
            await response.reply("❌ Cancelled.")
            raise Exception("Cancelled")
        return response.text.strip()

    try:
        # Ask for referral link
        referral_text = await ask("🔗 Sᴇɴᴅ ʀᴇꜰᴇʀᴀʟ ʟɪɴᴋ (like `https://t.me/username?start=173290`)")
        match = re.search(r"https://t\.me/([\w\d_]+)\?start=\d+", referral_text)
        if not match:
            await message.reply("❌ Invalid referral link format.")
            return
        username = match.group(1).replace("_", "")
        name = f"[{username}](https://t.me/{match.group(1)}?start=173290)"
        ref_link = f"https://t.me/{match.group(1)}?start=173290"

        # Ask for category
        cat = await ask("🗂 Sᴇɴᴅ ᴄᴀᴛᴇɢᴏʀʏ (like `stars`, `premium`, or `stars and premium`)")

        # Ask for criteria
        cri = await ask("🎯 Sᴇɴᴅ ᴄʀɪᴛᴇʀɪᴀ (`game` | `refer`)")

        # Ask for verified
        ver = await ask("✔️ Iꜱ ʙᴏᴛ ᴠᴇʀɪꜰɪᴇᴅ? (`true` | `false`)")

        # Ask for validity
        val = await ask("🕐 Sᴇɴᴅ ᴠᴀʟɪᴅɪᴛʏ (`unknown` | `few days` | `today` | `expired`)")

        # Ask for per refer
        ref = await ask("🎁 Sᴇɴᴅ ᴘᴇʀ ʀᴇꜰᴇʀ ʀᴇᴡᴀʀᴅ (`1 star` | `2 star` | `3 star`)")

        # Ask for minimum withdrawal
        min = await ask("💸 Sᴇɴᴅ ᴍɪɴ ᴡɪᴛʜᴅʀᴀᴡ")

        # Ask for optional more info
        await message.reply("ℹ️ Sᴇɴᴅ ᴍᴏʀᴇ ɪɴꜰᴏ (or /skip to skip)", quote=True)
        more_response = await client.ask(message.chat.id, timeout=120)
        if more_response.text.lower() == "/cancel":
            await more_response.reply("❌ Cancelled.")
            return
        more = more_response.text if more_response.text.lower() != "/skip" else "N/A"

        # Final message
        final_text = f"""\
ɴᴇᴡ ʙᴏᴛ       : {name}
ᴄᴀᴛᴇɢᴏʀʏ      : {cat}
ᴄʀɪᴛᴇʀɪᴀ       : {cri}
ᴠᴇʀɪꜰɪᴇᴅ       : {ver}
ᴠᴀʟɪᴅɪᴛʏ       : {val}
ᴩᴇʀ ʀᴇꜰᴇʀ     : {ref}
ᴍɪɴ ᴡɪᴛʜᴅʀᴀᴡ  : {min}
ᴍᴏʀᴇ ɪɴꜰᴏ     : {more}

({cat.lower()})
🔗 {ref_link}"""

        await client.send_message(CHANNEL_ID, final_text, disable_web_page_preview=True)
        await message.reply("✅ ʙᴏᴛ ᴀᴅᴅᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!")

    except Exception as e:
        print("AddBot Cancelled or Failed:", e)
