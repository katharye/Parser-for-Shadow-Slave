from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from database import find_max_value, find_min_value

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Download chapters?'), KeyboardButton(text='Read here')],
    [KeyboardButton(text='Notifications?')]
],
    resize_keyboard=True,
    input_field_placeholder='Добро пожаловать в Мимика! Выберите действие:'
)

min_chapter = find_min_value()
max_chapter = find_max_value()

async def navigation(current_chapter):
    keyboard = InlineKeyboardBuilder()
    
    if current_chapter > min_chapter:
        keyboard.add(InlineKeyboardButton(text='Previous', callback_data='prev'))

    if current_chapter < max_chapter:
        keyboard.add(InlineKeyboardButton(text='Next', callback_data='next'))

    return keyboard.as_markup()


chapters = [str(i) for i in range(max_chapter, min_chapter - 1, -1)]
async def reply_chapters():
    global chapters
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text='Go back'))
    for chapter in chapters:
        keyboard.add(KeyboardButton(text=chapter))
    return keyboard.adjust(1, 5).as_markup()