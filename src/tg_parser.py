import os
import re 
import random 

import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient

import tgf_parser

PATTERN = r"https://telegra.ph/Glava-\d+-.*-\d{2}-\d{2}"
TARGET = "Теневой Раб | Онгоинг"

load_dotenv()
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

if not api_id or not api_hash:
    raise ValueError("Missing API_ID or API_HASH in .env file")

api_id = int(api_id)

async def main():
    async with TelegramClient("parser", api_id, api_hash) as client:

        dialogs = await client.get_dialogs()

        for dialog in dialogs:
            if dialog.title == TARGET:
                messages = client.iter_messages(dialog)

                message_count = 0
                async for message in messages: 
                    if message.text is None:
                        continue

                    match = re.search(PATTERN, message.text)
                    if match is None:
                        continue

                    await asyncio.to_thread(tgf_parser.parsChapter, match.group())
                    message_count += 1
                    
                    await asyncio.sleep(random.uniform(0.3, 0.8))
                    if message_count % 10 == 0:
                        await asyncio.sleep(random.uniform(1.0, 3.0))
                break


asyncio.run(main())
