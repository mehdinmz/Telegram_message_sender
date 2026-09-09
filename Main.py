from telethon import TelegramClient , events
from telethon import functions
import os
import asyncio
from dotenv import load_dotenv
#Load environment variables from .env file
load_dotenv()

API_ID = int(os.environ["api_id"])
API_HASH = os.environ["api_hash"]
session = "session"
#start the client
client = TelegramClient(session, API_ID, API_HASH)

@client.on(events.NewMessage(pattern="/help", func=lambda e: e.is_private))
async def help_cmd(event: events.NewMessage.Event):
    await event.respond(
        "Use /new_msg <message> to send a new message to your targets"
    )

@client.on(events.NewMessage(pattern="/new_msg", func=lambda e: e.is_private))
async def new_msg_handler(event):
    # Check whether the sender is authorized
    # if event.sender_id not in ALLOWED_IDS:
    #     return

    # Get message text
    message = event.raw_text.split(" ", 1)[1] if len(event.raw_text.split(" ", 1)) > 1 else None
    sent = 0  
    skipped = 0
    failed = 0
    if not message:
        await event.reply(
            "Usage:\n"
            "/new_msg <message>"
        )
        return

     # Get Telegram contacts
    result = await client(
        functions.contacts.GetContactsRequest(hash=0)
    )

    contacts = result.users

    sent = 0
    failed = 0
    skipped = 0
    n = 0
    for contact in contacts:
        if n < 1 :
            n+=1
            # Skip bots
            if contact.bot:
                skipped += 1
                continue

            # Skip deleted accounts
            if contact.deleted:
                skipped += 1
                continue

            try:
                await client.send_message(
                    contact,
                    message
                )

                sent += 1

                # 2 second delay
                await asyncio.sleep(2)

            except Exception as e:
                failed += 1
                print(
                    f"Failed to send to {contact.id}: {e}"
                )

    await event.reply(
        f"Finished.\n\n"
        f"Sent: {sent}\n"
        f"Failed: {failed}\n"
        f"Skipped: {skipped}"
    )
if __name__ == "__main__":
    client.start()
    print("Bot is running...")
    client.run_until_disconnected()
