from users import init_users_db
from database import init_db

init_users_db()
init_db()

import logging 
import asyncio

from loader import dp, bot

from app.handlers import router

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)
    

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')