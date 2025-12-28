import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

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

async def safe_send(client, **kwargs):
    while True:
        try:
            return await client.send_cached_media(**kwargs)
        except FloodWait as e:
            await asyncio.sleep(e.value + 1)
          

@Client.on_message(filters.document | filters.video | filters.audio)
async def auto_frward(client, message):
    media = getattr(message, message.media.value, None)
    if not media:
        return

    await safe_send(
        client,
        chat_id=-1002518698743,
        file_id=media.file_id,
        caption=message.caption or ""
    )


@Client.on_chat_member_updated(filters.chat_type.channel)
async def bot_added_channel(client, update):
    if update.new_chat_member and update.new_chat_member.user.is_self:
        chat = update.chat
        text = (
            "➕ **Bot Added to Channel**\n\n"
            f"📛 Name: {chat.title}\n"
            f"🆔 ID: `{chat.id}`\n"
            f"📢 Type: Channel"
        )
        await client.send_message(1733124290, text)


@Client.on_message(filters.new_chat_members)
async def bot_added_group(client, message):
    for m in message.new_chat_members:
        if m.id == (await client.get_me()).id:
            chat = message.chat
            text = (
                "➕ **Bot Added to Group**\n\n"
                f"📛 Name: {chat.title}\n"
                f"🆔 ID: `{chat.id}`\n"
                f"👥 Type: {chat.type}"
            )
            await client.send_message(1733124290, text)
          
      
