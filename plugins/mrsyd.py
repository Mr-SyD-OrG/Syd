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


