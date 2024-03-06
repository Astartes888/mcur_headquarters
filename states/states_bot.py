from aiogram.fsm.state import State, StatesGroup


class FSM_bot(StatesGroup):
    type_mess = State()
    address_app = State()
    name_app = State()
    phone_num = State()
    problem = State()
    staff_name = State()
    end_reg = State()
    close_app = State()