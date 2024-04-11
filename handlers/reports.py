from aiogram import Router
from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.filters import Text, StateFilter
from aiogram.utils.chat_action import ChatActionSender
from aiogram.exceptions import TelegramBadRequest

from states.states_bot import FSM_bot
from bot_init import bot, client_for_evening_report, client_for_morning_report
from buttons.button_factory import get_inline_markup
from text.message import bot_reply
from utils import BasicTools

router = Router()


@router.callback_query(Text(text='evening_report'), StateFilter(default_state))
async def generate_evening_report(callback: CallbackQuery):
    inline_keyboard = await get_inline_markup(2, 
                                              'new_app', 
                                              'close',
                                              'morning_report',
                                              'evening_report',
                                              )
    async with ChatActionSender(bot=bot, chat_id=callback.message.chat.id):
        report = client_for_evening_report.prepare_evening_report()
        await callback.message.edit_text(report, parse_mode='HTML')
        await callback.message.answer(bot_reply['choice'], reply_markup=inline_keyboard)
        await callback.answer()


@router.callback_query(Text(text='morning_report'), StateFilter(default_state))
async def generate_morning_report(callback: CallbackQuery, state: FSMContext):
    inline_keyboard = await get_inline_markup(1, 'create', 'cancel')
    await state.set_state(FSM_bot.morning_rep)
    await callback.message.edit_text(bot_reply['await_messages'], reply_markup=inline_keyboard)
    await state.update_data(message_id=callback.message.message_id)
    await callback.answer()


@router.callback_query(Text(text='create'), StateFilter(FSM_bot.morning_rep))
async def sending_morning_report(callback: CallbackQuery, state: FSMContext):
    inline_keyboard = await get_inline_markup(2, 
                                              'new_app', 
                                              'close',
                                              'morning_report',
                                              'evening_report',
                                              )
    extracted_data = await state.get_data()
    async with ChatActionSender(bot=bot, chat_id=callback.message.chat.id):
        report = client_for_morning_report.prepare_morning_report(extracted_data)
        await callback.message.edit_text(report, parse_mode='HTML')
        await callback.message.answer(bot_reply['choice'], reply_markup=inline_keyboard)

        ids_for_delete = [BasicTools.finding_id_in_datakey(key) for key in extracted_data.keys()]
        for id in ids_for_delete:
            if id > 0:
                await bot.delete_message(chat_id=callback.message.chat.id, 
                                         message_id=id
                                         )
                
    await state.clear()
    await callback.answer()


@router.message(F.content_type == 'document', StateFilter(FSM_bot.morning_rep))
async def geting_xlsx_from_message(message: Message, state: FSMContext):
    file_id = message.document.file_id
    file_name = message.document.file_name
    file_io = await bot.download(file_id)
    data_key = {f'data_file_{message.message_id}': [file_io, file_name]}
    await state.update_data(**data_key)


@router.message(StateFilter(FSM_bot.morning_rep))
async def gathering_messages_for_parsing(message: Message, state: FSMContext):
    message_for_edit = await state.get_data()
    inline_keyboard = await get_inline_markup(1, 'create', 'cancel')
    data_key = {f'data_message_{message.message_id}': message.text}
    await state.update_data(**data_key)
    async with ChatActionSender(bot=bot, chat_id=message.chat.id):
        try:
            await bot.edit_message_text(text=bot_reply['start_create'], 
                                        chat_id=message.chat.id, 
                                        message_id=message_for_edit.get('message_id'),
                                        reply_markup=inline_keyboard 
                                        )
        except TelegramBadRequest:
            pass