import asyncio

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError

import app.keyboards as kb
import users as usr
from database import get_chapter_file, find_max_value
from tg_parser import overwrite_all, update
from loader import bot

MAX_LENGTH = 4096

router = Router()


class choosenChapter(StatesGroup):
    number = State()

class downloadChapters(StatesGroup):
    first = State()
    second = State()


def split_text(text: str, n: int = MAX_LENGTH):
    parts = []

    while len(text) > n:
        split_pos = text.rfind('\n', 0, n)
        if split_pos == -1:
            split_pos = text.rfind(' ', 0, n)
            if split_pos == -1:
                split_pos = n

        parts.append(text[:split_pos].rstrip())
        text = text[split_pos:].lstrip()

    if text:
        parts.append(text)

    return parts

async def send_to_all_subscribers(text: str):
    users = usr.get_all_user_ids()
    if not users:
        return
    for user in users:
        if usr.get_user_notifications_subscription(user):
            try:
                await bot.send_message(user, text)
                await asyncio.sleep(0.05)

            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after)
                try:
                    await bot.send_message(user, text)
                except Exception as e:
                    print(f"ERROR WITH USER <{user}: {e}>")

            except TelegramForbiddenError:
                await usr.update_user_notifications_subscription(user_id=user, notifications=False)

            except Exception as e:
                print(f"ERROR WITH USER <{user}: {e}>")

# async def merge_txt_files(first: int, second: int) -> bool:
#     with 
#     for chapter in range(first, second):


#----------------------------#
@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    await message.answer('Hello', reply_markup=await kb.main(user_id))
    usr.add_user_in_db(user_id)
#----------------------------#

#----------------------------#
@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer('Help', reply_markup=kb.navigation)

@router.message(Command('popa'))
async def popa_photo(message: Message):
    await message.answer_photo(photo='https://img.freepik.com/free-photo/beautiful-shot-white-british-shorthair-kitten_181624-57681.jpg',
                               caption='You are just popped!')
    await send_to_all_subscribers("POPAAAAA")
#----------------------------#

#----------------------------#
@router.callback_query(F.data == 'prev')
async def previous_chapter(callback: CallbackQuery):
    await callback.answer('')

    current_chapter = usr.get_user_chapter(callback.from_user.id)
    chapter_path = get_chapter_file(current_chapter - 1)
    with open(chapter_path, "r", encoding="utf-8") as f:
        text = f.read()

    parts = split_text(text)
    for part in parts[:-1]:
        await callback.message.answer(part)

    current_chapter -= 1
    usr.update_user_chapter(callback.from_user.id, current_chapter)
    await callback.message.answer(parts[-1], reply_markup=await kb.navigation(current_chapter))

@router.callback_query(F.data == 'next')
async def next_chapter(callback: CallbackQuery):
    await callback.answer('')

    current_chapter = usr.get_user_chapter(callback.from_user.id)
    chapter_path = get_chapter_file(current_chapter + 1)
    with open(chapter_path, "r", encoding="utf-8") as f:
        text = f.read()

    parts = split_text(text)
    for part in parts[:-1]:
        await callback.message.answer(part)

    current_chapter += 1
    usr.update_user_chapter(callback.from_user.id, current_chapter)
    await callback.message.answer(parts[-1], reply_markup=await kb.navigation(current_chapter))
#----------------------------#

#----------------------------#
@router.message(F.text == 'Read here')
async def choose_read_chapter_message(message: Message, state: FSMContext):
    await message.delete()
    await state.set_state(choosenChapter.number)
    await kb.find_extreme_chapters()
    await message.answer(text=f'Choose a chapter between {kb.min_chapter} and {kb.max_chapter}', reply_markup=kb.go_back)

@router.callback_query(F.data == 'choose')
async def choose_read_chapter_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(choosenChapter.number)
    await kb.find_extreme_chapters()
    await callback.message.answer(text=f'Choose a chapter between {kb.min_chapter} and {kb.max_chapter}', reply_markup=kb.go_back)
    await callback.answer()

@router.message(choosenChapter.number)
async def finish_choosing(message: Message, state: FSMContext):
    user_input = message.text.strip()
    await message.delete()

    if user_input == 'Go back':
        
        await state.clear()
        await message.answer("Back to menu:", reply_markup=await kb.main(message.from_user.id))
        return

    if not user_input.isdigit():
        await message.answer('Incorrect chapter! Choose again', reply_markup=kb.go_back)
        return
    
    chapter_number = int(user_input)
    if not (kb.min_chapter <= chapter_number <= kb.max_chapter):
        await message.answer('Incorrect chapter! Choose again', reply_markup=kb.go_back)
        return
    
    await state.update_data(number=chapter_number)
    data = await state.get_data()

    try:
        chapter_path = get_chapter_file(chapter_number)
        with open(chapter_path, "r", encoding="utf-8") as f:
            text = f.read()
    
        parts = split_text(text)
        for part in parts[:-1]:
            await message.answer(part, reply_markup=ReplyKeyboardRemove())

        await state.clear()
        usr.update_user_chapter(message.from_user.id, chapter_number)
        current_chapter = usr.get_user_chapter(message.from_user.id)
        await message.answer(parts[-1], reply_markup=await kb.navigation(current_chapter)) 
    except:
        await message.answer('ERROR')
#----------------------------#
    
#----------------------------#
# @router.message(F.text == 'Download chapters')
async def download_chapters(message: Message, state: FSMContext):
    await message.delete()
    await state.set_state(downloadChapters.first)
    await kb.find_extreme_chapters()
    await message.answer(text=f'Choose first chapter between {kb.min_chapter} and {kb.max_chapter}', reply_markup=kb.go_back)

# @router.message(downloadChapters.first)
async def first(message: Message, state: FSMContext):
    user_input = message.text.strip()
    if user_input == 'Go back':
        await message.delete()
        await state.clear()
        await message.answer("Back to menu:", reply_markup=await kb.main(message.from_user.id))
        return

    if not user_input.isdigit():
        await message.answer('Incorrect chapter! Choose again', reply_markup=kb.go_back)
        return
    
    chapter_number = int(user_input)
    if not (kb.min_chapter <= chapter_number <= kb.max_chapter):
        await message.answer('Incorrect chapter! Choose again', reply_markup=kb.go_back)
        return
    
    await state.update_data(first=chapter_number)
    await state.set_state(downloadChapters.second)
    await kb.find_extreme_chapters()
    await message.answer(text=f'Choose second chapter between {kb.min_chapter} and {kb.max_chapter}', reply_markup=kb.go_back)

# @router.message(downloadChapters.second)
async def second(message: Message, state: FSMContext):
    user_input = message.text.strip()
    

    if user_input == 'Go back':
        await message.delete()
        await state.clear()
        await message.answer("Back to menu:", reply_markup=await kb.main(message.from_user.id))
        return

    if not user_input.isdigit():
        await message.answer('Incorrect chapter! Choose again', reply_markup=kb.go_back)
        return
    
    chapter_number = int(user_input)
    if not ((kb.min_chapter <= chapter_number <= kb.max_chapter)):
        await message.answer('Incorrect chapter! Choose again', reply_markup=kb.go_back)
        return
    
    await state.update_data(second=chapter_number)
    
    data = await state.get_data()
    if data['first'] > data['second']:
        data['first'], data['second'] = data['second'], data['first']



    await state.clear()
#----------------------------#

#----------------------------#
@router.message(F.text == 'Notifications: ❎')
async def notifications_on(message: Message):
    await message.delete()
    await asyncio.sleep(0.2)

    try:
        user_id = message.from_user.id
        if usr.update_user_notifications_subscription(user_id, True):
            await message.answer("Notifications: ON", reply_markup=await kb.main(user_id))
    except:
        await message.answer("ERROR")

@router.message(F.text == 'Notifications: ✅')
async def notifications_off(message: Message):
    await message.delete()
    await asyncio.sleep(0.2)

    try:
        user_id = message.from_user.id
        if usr.update_user_notifications_subscription(user_id, False):
            await message.answer("Notifications: OFF", reply_markup=await kb.main(user_id))
    except:
        await message.answer("ERROR")
#----------------------------#

#----------------------------#
@router.message(F.text == 'Rewrite ALL')
async def rewrite_all_data(message: Message):
    m = await message.answer("⏳ Rewriting all chapters...")
    await asyncio.sleep(0.5)
    await m.edit_text("⏳ Rewriting all chapters..")
    await asyncio.sleep(0.5)
    await m.edit_text("⏳ Rewriting all chapters...")
    await overwrite_all()
    await m.edit_text("✅ Rewrite complete!")
    await message.answer("Back to menu:", reply_markup=await kb.main(message.from_user.id))

@router.message(F.text == 'Update data')
async def update_data(message: Message):
    max_chapter_before = find_max_value()
    await update()
    max_chapter_after = find_max_value()

    if max_chapter_before < max_chapter_after:
        await message.answer("Chapters succesfully updated!")
        await send_to_all_subscribers("New chapters are now available!")
#----------------------------#