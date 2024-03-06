from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.state import default_state
from aiogram.filters import Text, StateFilter
from aiogram.utils.chat_action import ChatActionSender

from bot_init import bot, client_for_reports
from buttons.button_factory import get_inline_markup
from text.message import bot_reply

router = Router()


@router.callback_query(Text(text='report'), StateFilter(default_state))
async def generate_report( callback: CallbackQuery):
    inline_keyboard = await get_inline_markup(1, 'new_app', 'report', 'close')
    async with ChatActionSender(bot=bot, chat_id=callback.message.chat.id):
        report = client_for_reports.prepare_report()
        await callback.message.edit_text(report, parse_mode='HTML')
        await callback.message.answer(bot_reply['choice'], reply_markup=inline_keyboard)
        await callback.answer()