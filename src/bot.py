from users import init_users_db
from database import init_db
from app.auto_check import auto_check_chapters

init_users_db()
init_db()

import logging 
import asyncio

from loader import dp, bot

from app.handlers import router

async def main():
    dp.include_router(router)

    stop_event = asyncio.Event()
    checker_task = asyncio.create_task(auto_check_chapters(stop_event=stop_event))
    
    try:
        await dp.start_polling(bot)
    finally:
        stop_event.set()
        checker_task.cancel()
        try:
            await checker_task
        except asyncio.CancelledError:
            pass

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')