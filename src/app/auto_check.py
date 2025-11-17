import asyncio
from datetime import datetime
import zoneinfo

from tg_parser import update
from database import find_max_value
from app.handlers import send_to_all_subscribers

async def auto_check_chapters(stop_event: asyncio.Event, 
                              tz_name: str = "Europe/Moscow", 
                              interval_seconds: int = 600):
    tz = zoneinfo.ZoneInfo(tz_name)

    try:
        while True:
            now = datetime.now(tz)
            if now.hour == 20:
                last_chapter = find_max_value()
                try:
                    await update()
                    if find_max_value() > last_chapter:
                        await send_to_all_subscribers('New chapters are now available!')
                except Exception as e:
                    print(f'Error with func: {e}')
            
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=interval_seconds)
                break
            except asyncio.TimeoutError:
                continue
                    
    except asyncio.CancelledError:
        pass