from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.filters import Text, StateFilter
from aiogram.utils.chat_action import ChatActionSender

from bot_init import bot, client_for_registration
from states.states_bot import FSM_bot
from buttons.button_factory import get_inline_markup
from text.message import bot_reply
from utils.tools import BasicTools

router = Router()


@router.callback_query(Text(text='close'), StateFilter(default_state))
async def asking_appeals_number(callback: CallbackQuery, state: FSMContext):
    inline_keyboard = await get_inline_markup(1, 'cancel')
    await state.set_state(FSM_bot.close_app)
    await callback.message.edit_text(bot_reply['app_num'], reply_markup=inline_keyboard)
    await state.update_data(message_id=callback.message.message_id)
    await callback.answer()


@router.message(StateFilter(FSM_bot.close_app))
async def closing_appeals(message: Message, state: FSMContext):
    message_for_edit = await state.get_data()
    if BasicTools.check_appeals_number(message.text) == False:
        inline_keyboard = await get_inline_markup(1, 'cancel')
        await bot.edit_message_text(text=bot_reply['wrong_app_num'], 
                                    chat_id=message.chat.id, 
                                    message_id=message_for_edit.get('message_id'), 
                                    reply_markup=inline_keyboard)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        return
    await state.update_data(app_nums=BasicTools.format_appeals_number(message.text))
    inline_keyboard = await get_inline_markup(2, 
                                              'new_app', 
                                              'close',
                                              'morning_report',
                                              'evening_report',
                                              )
    extracted_nums = await state.get_data()
    async with ChatActionSender(bot=bot, chat_id=message.chat.id):
        closed_appeals = client_for_registration.close_appeals(extracted_nums)
        await bot.edit_message_text(text=closed_appeals, 
                                    chat_id=message.chat.id, 
                                    message_id=message_for_edit.get('message_id'), 
                                    )
        await message.answer(bot_reply['choice'], reply_markup=inline_keyboard)
        await state.clear()
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)