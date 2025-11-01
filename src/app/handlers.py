from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
from database import get_chapter_file, find_max_value, find_min_value
from users import add_user_in_db, get_user_chapter, update_user_chapter

MAX_LENGTH = 4096
current_chapter = 0

router = Router()

def split_text(text: str, n: int = MAX_LENGTH):
    lines = text.split('\n')
    parts = []
    current_part = ''

    for line in lines:
        if len(line) + len(current_part) + 1 <= n:
            current_part += line + '\n'
        else:
            parts.append(current_part.rstrip('\n'))
            current_part = line + '\n'
    
    if current_part:
        parts.append(current_part.rstrip("\n"))

    return parts



@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Hello', reply_markup=kb.main)
    add_user_in_db(message.from_user.id)

@router.message(F.text == 'Go back')
async def cmd_start(message: Message):
    await message.answer('Hello', reply_markup=kb.main)


@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer('Help', reply_markup=kb.navigation)


@router.message(Command('popa'))
async def popa_photo(message: Message):
    await message.answer_photo(photo='https://img.freepik.com/free-photo/beautiful-shot-white-british-shorthair-kitten_181624-57681.jpg',
                               caption='You are just popped!')

@router.callback_query(F.data == 'prev')
async def previous_chapter(callback: CallbackQuery):
    await callback.answer('')

    current_chapter = get_user_chapter(callback.from_user.id)
    chapter_path = get_chapter_file(current_chapter - 1)
    with open(chapter_path, "r", encoding="utf-8") as f:
        text = f.read()

    parts = split_text(text)
    for part in parts[:-1]:
        await callback.message.answer(part)

    current_chapter -= 1
    update_user_chapter(callback.from_user.id, current_chapter)
    await callback.message.answer(parts[-1], reply_markup=await kb.navigation(current_chapter))

@router.callback_query(F.data == 'next')
async def next_chapter(callback: CallbackQuery):
    await callback.answer('')

    current_chapter = get_user_chapter(callback.from_user.id)
    chapter_path = get_chapter_file(current_chapter + 1)
    with open(chapter_path, "r", encoding="utf-8") as f:
        text = f.read()

    parts = split_text(text)
    for part in parts[:-1]:
        await callback.message.answer(part)

    current_chapter += 1
    update_user_chapter(callback.from_user.id, current_chapter)
    await callback.message.answer(parts[-1], reply_markup=await kb.navigation(current_chapter))
    

@router.message(F.text == 'Read here')
async def choose_read_chapter(message: Message):
    await message.answer(text='Choose a chapter', reply_markup=await kb.reply_chapters())

@router.message()
async def display_chapter(message: Message):
    ignored = ['Go back', 'popa', 'Read here']
    if message.text in ignored:
        return

    chapter_path = get_chapter_file(message.text)
    try:
        with open(chapter_path, "r", encoding="utf-8") as f:
            text = f.read()
    
        parts = split_text(text)
        for part in parts[:-1]:
            await message.answer(part)
        update_user_chapter(message.from_user.id, int(message.text))
        current_chapter = get_user_chapter(message.from_user.id)
        await message.answer(parts[-1], reply_markup=await kb.navigation(current_chapter)) 
    except:
        await message.answer('Incorrect chapter! Choose again', reply_markup=await kb.reply_chapters())
