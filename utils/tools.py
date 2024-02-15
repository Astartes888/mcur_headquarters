import re
from datetime import datetime


def check_phone_number(message : str) -> bool:
    if message in "Нет номера":
        return True
    else:
        clear_number = re.sub(r'[\W_]', '', message)
        if len(clear_number) >= 10 and len(clear_number) <= 11:
            return clear_number.isdigit()
        else:
            return False


def format_phone_number(message : str) -> str:
    if message in "Нет номера":
        return message
    else:
        clear_number = re.sub(r'[\W_]', ' ', message)
        return clear_number


def ending_of_word(ammount):
    var_1 = lambda x: (x%100)//10 != 1 and x%10 == 1
    var_2 = lambda x: (x%100)//10 != 1 and x%10 in [2, 3, 4]
    return 'обращение' if var_1(ammount) else 'обращения' if var_2(ammount) else 'обращений'


def get_currenttime() -> str:
    return datetime.today().strftime('%d.%m.%Y')