from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.filters import Text, Command, CommandStart, StateFilter, or_f
from aiogram.methods.send_chat_action import SendChatAction

from bot_init import bot, client_for_registration, client_for_reports
from states.states_bot import FSM_bot
from buttons.button_factory import get_inline_markup
from text.button import messenger_type, staff_list, button_text
from text.message import bot_reply, end_reg_text
from utils.tools import check_phone_number, format_phone_number


router = Router()


@router.message(CommandStart(), StateFilter(default_state))
async def register_application(message: Message, state: FSMContext):
    inline_keyboard = await get_inline_markup(1, 'new_app', 'report')
    await message.answer(bot_reply['choice'], reply_markup=inline_keyboard)


@router.message(or_f(Command(commands='cancel'), 
                     Text(text=('отмена', 'Отмена ❌'), ignore_case=True)
                     ), 
                     ~StateFilter(default_state)
                     )
async def reg_cancel(message: Message, state: FSMContext):
    inline_keyboard = await get_inline_markup(1, 'new_app', 'report')
    await message.answer(bot_reply['choice'], reply_markup=inline_keyboard)
    await state.clear()
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@router.callback_query(lambda CallbackQuery: CallbackQuery.data=='cancel')
async def reg_cancel_inline(callback: CallbackQuery, state: FSMContext):
    inline_keyboard = await get_inline_markup(1, 'new_app', 'report')
    await callback.message.edit_text(bot_reply['cancel'], reply_markup=inline_keyboard)
    await state.clear()
    await callback.answer()


@router.callback_query(Text(text='report'), StateFilter(default_state))
async def generate_report(callback: CallbackQuery):
    inline_keyboard = await get_inline_markup(1, 'new_app', 'report')
    await bot(SendChatAction(chat_id=callback.message.chat.id, action='typing'))
    report = client_for_reports.prepare_report()
    await callback.message.edit_text(report, parse_mode='HTML')
    await callback.message.answer(bot_reply['choice'], reply_markup=inline_keyboard)
    await callback.answer()


@router.callback_query(Text(text='new_app'), StateFilter(default_state))
async def choice_type_of_messenger(callback: CallbackQuery, state: FSMContext):
    inline_keyboard = await get_inline_markup(3, *messenger_type)
    await state.set_state(FSM_bot.type_mess)
    await callback.message.edit_text(bot_reply['type_mess'], reply_markup=inline_keyboard)
    await callback.answer()


@router.callback_query(StateFilter(FSM_bot.type_mess))
async def fill_application_adress(callback: CallbackQuery, state: FSMContext):
    await state.update_data(type=callback.data)
    await state.set_state(FSM_bot.address_app)
    inline_keyboard = await get_inline_markup(1, 'cancel')
    await callback.message.edit_text(bot_reply['address'], reply_markup=inline_keyboard)
    await state.update_data(message_id=callback.message.message_id)


@router.message(StateFilter(FSM_bot.address_app))
async def fill_applicant_name(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(FSM_bot.name_app)
    message_for_edit = await state.get_data()
    inline_keyboard = await get_inline_markup(1, 'cancel')
    await bot.edit_message_text(bot_reply['name'], 
                                chat_id=message.chat.id, 
                                message_id=message_for_edit.get('message_id'), 
                                reply_markup=inline_keyboard)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@router.message(StateFilter(FSM_bot.name_app))
async def fill_phone_number(message: Message, state: FSMContext):
    inline_keyboard = await get_inline_markup(1, 'no_phone', 'cancel')
    await state.update_data(name=message.text)
    await state.set_state(FSM_bot.phone_num)
    message_for_edit = await state.get_data()
    await bot.edit_message_text(bot_reply['phone_num'], 
                                chat_id=message.chat.id, 
                                message_id=message_for_edit.get('message_id'), 
                                reply_markup=inline_keyboard)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@router.callback_query(StateFilter(FSM_bot.phone_num))
async def fill_applicant_problem_from_inline(callback: CallbackQuery, state: FSMContext):
    await state.update_data(phone=button_text[callback.data])
    await state.set_state(FSM_bot.problem)
    message_for_edit = await state.get_data()
    inline_keyboard = await get_inline_markup(1, 'cancel')
    await bot.edit_message_text(bot_reply['problem'], 
                                chat_id=callback.message.chat.id, 
                                message_id=message_for_edit.get('message_id'), 
                                reply_markup=inline_keyboard)
    await callback.answer()


@router.message(StateFilter(FSM_bot.phone_num))
async def fill_applicant_problem(message: Message, state: FSMContext):
    message_for_edit = await state.get_data()
    if check_phone_number(message.text) == False:
        inline_keyboard = await get_inline_markup(1, 'no_phone', 'cancel')
        await bot.edit_message_text(bot_reply['wrong_phone_num'], 
                                    chat_id=message.chat.id, 
                                    message_id=message_for_edit.get('message_id'), 
                                    reply_markup=inline_keyboard)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        return
    await state.update_data(phone=format_phone_number(message.text))
    await state.set_state(FSM_bot.problem)
    inline_keyboard = await get_inline_markup(1, 'cancel')
    await bot.edit_message_text(bot_reply['problem'], 
                                chat_id=message.chat.id, 
                                message_id=message_for_edit.get('message_id'), 
                                reply_markup=inline_keyboard)
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)


@router.message(StateFilter(FSM_bot.problem))
async def select_staff_name(message: Message, state: FSMContext):
    inline_keyboard = await get_inline_markup(1, **staff_list)
    await state.update_data(problem=message.text.capitalize())
    await state.set_state(FSM_bot.staff_name)
    message_for_edit = await state.get_data()
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await bot.edit_message_text(bot_reply['choose_staff'], 
                                chat_id=message.chat.id, 
                                message_id=message_for_edit.get('message_id'), 
                                reply_markup=inline_keyboard)


@router.callback_query(StateFilter(FSM_bot.staff_name))
async def end_of_registration(callback: CallbackQuery, state: FSMContext):
    await state.update_data(staff=staff_list[callback.data])
    inline_keyboard = await get_inline_markup(1, 'new_app', 'report')
    reg_data = await state.get_data()
    await bot.send_chat_action(callback.message.chat.id, 'typing')

    # тут вызов функции записи данных в гугл таблицу, возвращающая номер обращения.
    application_num = client_for_registration.update_worksheet_row(reg_data) 
    await callback.message.edit_text(end_reg_text.format(application_num), reply_markup=inline_keyboard)
    await callback.answer()
    await state.clear()
