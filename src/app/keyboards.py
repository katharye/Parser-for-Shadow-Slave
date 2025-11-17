from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from database import find_max_value, find_min_value
from users import get_user_notifications_subscription

min_chapter = max_chapter = 992

async def find_extreme_chapters():
    global min_chapter, max_chapter 
    min_chapter = find_min_value()
    max_chapter = find_max_value()

async def main(user_id):
    keyboard = ReplyKeyboardBuilder()

    keyboard.add(KeyboardButton(text='Download chapters'))
    keyboard.add(KeyboardButton(text='Read here'))

    if get_user_notifications_subscription(user_id):
        keyboard.add(KeyboardButton(text='Notifications: ✅'))
    else:
        keyboard.add(KeyboardButton(text='Notifications: ❎'))


    if user_id in [1498219587, 8264374103, 1180202795]:
        keyboard.add(KeyboardButton(text='Rewrite ALL'))
        keyboard.add(KeyboardButton(text='Update data'))
    
    return keyboard.adjust(2, 1, 2).as_markup(
        resize_keyboard=True,
        input_field_placeholder='Welcome! Choose option:'
    )

async def navigation(current_chapter):
    keyboard = InlineKeyboardBuilder()
    
    keyboard.add(InlineKeyboardButton(text='Choose a chapter', callback_data='choose'))

    if current_chapter > min_chapter:
        keyboard.add(InlineKeyboardButton(text='Previous', callback_data='prev'))

    if current_chapter < max_chapter:
        keyboard.add(InlineKeyboardButton(text='Next', callback_data='next'))

    return keyboard.adjust(1, 2).as_markup()

go_back = ReplyKeyboardMarkup(
    keyboard=[
    [KeyboardButton(text='Go back')]
    ],
    resize_keyboard=True
)
