from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton, 
                          ReplyKeyboardMarkup, KeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from text.button import button_text


async def get_inline_markup(width: int, *args, **kwargs) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons = []
    # Заполняем список кнопками из аргументов args и kwargs
    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=button_text[button] if button in button_text else button,
                callback_data=button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))
    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)
    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()

async def get_markup(width: int, *args, resize=False, one_time=False, input_field=None, **kwargs) -> ReplyKeyboardMarkup:

    kb_builder = ReplyKeyboardBuilder()

    buttons = []

    if args:
        for button in args:
            buttons.append(KeyboardButton(
                text=button_text[button] if button in button_text else button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(KeyboardButton(text=text))

    kb_builder.row(*buttons, width=width)

    return kb_builder.as_markup(resize_keyboard=resize, one_time_keyboard=one_time, input_field_placeholder=input_field)