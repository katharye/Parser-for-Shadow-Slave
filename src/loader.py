import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

load_dotenv()
bot_token = os.getenv("BOT_TOKEN")

bot = Bot(token=bot_token)
dp = Dispatcher()