import re
from datetime import datetime

class BasicTools:

    @staticmethod
    def format_appeals_number(message: str) -> str:
        clear_number = re.sub(r'[\W_]', ' ', message)
        ready_number = re.sub(r'\s+', ' ', clear_number)
        return ready_number

    @staticmethod
    def check_appeals_number(message: str) -> bool:
        clear_number = re.sub(r'[\W_]', '', message)
        return clear_number.isdigit()

    @staticmethod
    def check_phone_number(message: str) -> bool:
        if message in ("Нет номера", "нет номера"):
            return True
        else:
            clear_number = re.sub(r'[\W_]', '', message)
            if len(clear_number) >= 10 and len(clear_number) <= 11:
                return clear_number.isdigit()
            else:
                return False

    @staticmethod
    def format_phone_number(message: str) -> str:
        if message in ("Нет номера", "нет номера"):
            return message
        else:
            clear_number = re.sub(r'[\W_]', ' ', message)
            ready_number = re.sub(r'\s+', ' ', clear_number)
            return ready_number

    @staticmethod
    def ending_of_word(ammount: int) -> str:
        var_1 = lambda x: (x%100)//10 != 1 and x%10 == 1
        var_2 = lambda x: (x%100)//10 != 1 and x%10 in [2, 3, 4]
        return 'обращение' if var_1(ammount) else 'обращения' if var_2(ammount) else 'обращений'

    @staticmethod
    def get_currenttime() -> str:
        return datetime.today().strftime('%d.%m.%Y')