from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.filters import Text, Command, CommandStart, StateFilter, or_f

from bot_init import bot
from buttons.button_factory import get_inline_markup
from text.message import bot_reply

router = Router()


@router.message(CommandStart(), StateFilter(default_state))
async def register_application(message: Message):
    inline_keyboard = await get_inline_markup(1, 'new_app', 'report', 'close')
    await message.answer(bot_reply['choice'], reply_markup=inline_keyboard)


@router.message(or_f(Command(commands='cancel'), 
                     Text(text=('отмена', 'Отмена ❌'), ignore_case=True)
                     ), 
                     ~StateFilter(default_state)
                     )
async def reg_cancel(message: Message, state: FSMContext):
    inline_keyboard = await get_inline_markup(1, 'new_app', 'report', 'close')
    await message.answer(bot_reply['choice'], reply_markup=inline_keyboard)
    await state.clear()
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@router.callback_query(lambda CallbackQuery: CallbackQuery.data=='cancel')
async def reg_cancel_inline(callback: CallbackQuery, state: FSMContext):
    inline_keyboard = await get_inline_markup(1, 'new_app', 'report', 'close')
    await callback.message.edit_text(bot_reply['cancel'], reply_markup=inline_keyboard)
    await state.clear()
    await callback.answer()
