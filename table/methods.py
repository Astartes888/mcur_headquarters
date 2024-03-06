import logging
from logging import Logger
from typing import Optional

from pygsheets import authorize
from pygsheets.client import Client
from pygsheets.exceptions import PyGsheetsException, CellNotFound
from pygsheets import Cell

from text.message import report_text
from utils.tools import BasicTools


class CurrentSheet(Client):

    DEFAULT_PATH = '/mcur_headquarters/table/'
    DEFAULT_NAME = 'dump.txt'

    def __init__(self, key_path: str, 
                 table_key: str, 
                 index_sheet: int = 0, 
                 logger: Optional[Logger] = None,
                 dump_name: Optional[str] = None,
                 dump_path: Optional[str] = None
                 ) -> None:
        """
        :param key_path: путь до ключа сервисного аккаунта в формате json
        :param table_key: ключ Google таблицы
        :param index_sheet: индекс страницы в таблице
        :param logger: объект класса Logger
        :param dump_name: название файла дампа с расширением txt, где записываются номера обращений, по умолчанию 'dump.txt'
        :param dump_path: путь до файла с дампом, по умолчанию текущая рабочая директория
        """
        self.current_client = authorize(service_account_file=key_path, 
                                        seconds_per_quota=500
                                        )
        self.table = self.current_client.open_by_key(table_key)
        self.work_sheet = self.table.worksheet('index', index_sheet)
        self.logger = logger if logger is not None else logging.getLogger()
        self.dump_name = dump_name if dump_name is not None else self.DEFAULT_NAME
        self.dump_path = dump_path if dump_path is not None else self.DEFAULT_PATH
        self.full_path = self.dump_path + self.dump_name
        self.starting_index_of_row: Optional[int] = None
        self.ending_index_of_row: Optional[int] = None

    # Считываем наш дамп, хранящий в себе номер последней записанной строки
    # или создаём новый.
    def _read_dump(self) -> int|None:
        try:    
            with open(self.full_path, 'r') as file:
                index_of_row = file.read()
                if index_of_row:
                    return int(index_of_row)
                else:
                    return None
        except (FileNotFoundError, IOError) as err:
            if isinstance(err, FileNotFoundError):
                with open(self.full_path, 'w') as file:
                    pass
                self.logger.info(f'Создан файл дампа: {self.full_path}')
                return None
            else:
                self.logger.error(f'Не удалось прочитать дамп.\nПричина: {err}')
                return None
        
    # Сохраняем индекс заполненной строки в дамп.
    def _write_dump(self, index: int):
        try:
            with open(self.full_path, 'w') as file:
                file.write(str(index))
        except IOError as err:
            self.logger.error(f'Не удалось записать дамп.\nПричина: {err}')  

    # Делаем выборку по колонке "№ обращения" и по последнему элементу 
    # (строке) выясняем общее кол-во строк.
    def _get_last_index(self) -> int:
        try:
            fetched_column = self.work_sheet.get_col(1, include_tailing_empty=False)
            ending_index_of_row = int(fetched_column[-1]) + 1
            return ending_index_of_row
        except PyGsheetsException as err:
            self.logger.error(f'Неудалось выбрать колонку.\nПричина: {err}')

    def _fetch_row(self, index: int) -> list:
        try:
            return self.work_sheet.get_row(index)
        except PyGsheetsException as err:
            self.logger.error(f'Неудалось выбрать строку.\nПричина: {err}')

    # Делаем выборку строк в диапазоне. Колонки от A до N.
    def _fetch_values(self) -> list[list[str]]:
        start = f'A{self.starting_index_of_row}'
        end = f'N{self.ending_index_of_row}'
        try:
            return self.work_sheet.get_values(start, end, include_tailing_empty_rows=True)
        except PyGsheetsException as err:
            self.logger.error(f'Неудалось выбрать строки.\nПричина: {err}')

class CitizensAppeals(CurrentSheet):

    # Пытаемся взять из дампа номер индекса для определения начала поиска
    # строки.
    def _define_default_starting_index(self) -> int:
        readed_dump = self._read_dump()
        if readed_dump is None:
            return round(self._get_last_index() / 2)
        else:
            return readed_dump

    def _preparing_range_for_fetch_values(self):
        if self.starting_index_of_row is None:
            self.starting_index_of_row = self._define_default_starting_index()

        # +2 к общему кол-ву строк для увеличения диапазона поиска нужной строки  
        # в случае, если в изначальном диапазоне небыло нужной строки для
        # записи данных.
        self.ending_index_of_row = self._get_last_index() + 2

    def _color_the_row(self, app_nums: list[str], cells: list[Cell]):
        list_of_ranges = [f'A{int(num)+1}:N{int(num)+1}' for num in app_nums]
        # apply_format принимает диапазон или список деапазонов для форматирования,
        # вторым параметром идёт ячейка или список ячеек в качестве образца форматирования,
        # третим параметром идёт поле ячейки для обновления формата
        self.work_sheet.apply_format(list_of_ranges, cells, fields = "userEnteredFormat.backgroundColor")

    def _preparing_cells_for_update(self, app_nums: list[str]) -> list[Cell]:
        cell_color = (0.6627451, 0.8156863, 0.5568628, 0)
        list_of_cells = []
        for num in app_nums:
            ready_cell = Cell(f'L{int(num)+1}', 'Решено')
            ready_cell.color = cell_color
            list_of_cells.append(ready_cell)
        return list_of_cells

    def update_worksheet_row(self, value: dict) -> str:
        self._preparing_range_for_fetch_values()
        fetched_values = self._fetch_values()

        # Нумеруем выбранные строки аналогично их реальному индексу в таблице
        prepared_values = enumerate(fetched_values, start=self.starting_index_of_row)
        number_of_applications = ''
        for row_num, row in prepared_values: 
            row_for_check = row
            index = row_num
            # Каждый отрезок строки (необходимые колонки строки) конвентируем в  
            # булевы значения, чтобы определить - пригодна ли для записи вся строка 
            # (пустая ли строка).
            if all(True if i == '' else False for i in row_for_check[5:10]):
                ready_for_update_row = [
                    [
                        row_num - 1, BasicTools.get_currenttime(), value.get('type'), '', '',
                        value.get('address'), value.get('name'), value.get('phone'),
                        '', value.get('problem'), '', '', value.get('staff'), ''
                        ]
                        ]
                self.work_sheet.update_row(index, ready_for_update_row) 
                self.starting_index_of_row = index
                number_of_applications = str(row_num - 1)
                self._write_dump(index)
                break
        
        return number_of_applications
    
    def close_appeals(self, value: dict) -> str:
        list_of_app_numbers = value.get('app_nums').split(' ')
        list_of_cells = self._preparing_cells_for_update(list_of_app_numbers)
        sentence = 'Обращения {} были закрыты.' if len(list_of_app_numbers) > 1 else 'Обращение {} было закрыто.'
        try:
            self.work_sheet.update_values(cell_list=list_of_cells)
            self._color_the_row(list_of_app_numbers, list_of_cells)
            return sentence.format(', '.join(list_of_app_numbers))
        except CellNotFound as err:
            self.logger.error(f'Неудалось обновить ячейки.\nПричина: {err}')
            return 'Обращения не закрыты, возможно Вы не правильно указали их номер.'

class Reports(CurrentSheet):

    def _define_actual_indexes(self):
        starting_index = self.starting_index_of_row if self.starting_index_of_row\
              is not None else self._read_dump()
        # Выбираем колонку с датами регистрации.
        column_with_dates = self.work_sheet.get_col(2, include_tailing_empty=False)

        if starting_index:
            # Т.к. разница между индексом строки в таблице на 1 больше 
            # чем индекс в текущем списке column_with_dates, то и 
            # уменьшаем на эту единицу для корректного среза.
            starting_index = starting_index - 1
            column_with_dates = column_with_dates[starting_index:]
        else:
            starting_index = 0
        
        prepared_for_filter = enumerate(column_with_dates, start=starting_index)
        # index + 1 для возврата реального индекса строки в таблице,
        # чтобы в дальнейшем использовать их при выборке диапазона строк.
        filtred_column_with_dates = [index + 1 for index, date in prepared_for_filter\
                                      if date == BasicTools.get_currenttime()] 
        
        if filtred_column_with_dates:
            self.starting_index_of_row = filtred_column_with_dates[0]
            self.ending_index_of_row = filtred_column_with_dates[-1]
            self._write_dump(filtred_column_with_dates[0])
        else:
            self.starting_index_of_row = None
            self.ending_index_of_row = None

    def _prepare_range_for_fetch_values(self) -> bool:
        self._define_actual_indexes()
        if self.starting_index_of_row is None:
            return False
        else:
            return True

    def _sorting_by_executor(self, for_sorting: dict) -> dict:
        ready_dict = {}
        for key, value in for_sorting.items():
            sorted_value = sorted(value.items(), key=lambda x: x[1], reverse=True)
            ready_dict[key] = dict(sorted_value)
        return ready_dict

    def _sorting_by_type_of_work(self, for_sorting: dict) -> dict:
        ready_dict = sorted(for_sorting.items(), key=lambda x: x[1][0], reverse=True)
        return dict(ready_dict)
    
    def _prepare_entries(self) -> dict|None:
        # Проверяем - есть ли актуальный диапазон для выборки данных
        if not self._prepare_range_for_fetch_values():
            return None
        
        # Общее кол-во записей на текущую дату.
        self.total_appl = 0
        # Инициируем словарь, где основной ключ это вид работ,
        # а подсловарь это исполнитель и кол-во обращений по нему.
        type_of_work: dict[str: dict[str: int]] = {}

        range_of_rows = self._fetch_values()
        
        for row in range_of_rows:
            # Формируем готовую строку (списком) с нужным срезом данных
            # (тип работ и исполнитель). 
            ready_row = row[8:11:2]
            # Если в строке нет нужных записей, то переходим к следующей.
            if any(True if i == '' else False for i in ready_row):
                continue

            self.total_appl += 1
            # Проверка наличия типа работ в нашем общем словаре type_of_work, если есть, 
            # то проверка наличия исполнителя в подсловаре (если есть увеличиваем  
            # кол-во обращений по нему, если нет то добавляем исполнителя), если нет,
            # то добавляем тип работ в общий словарь. 
            if ready_row[0] in type_of_work:
                if ready_row[1] in type_of_work[ready_row[0]]:
                    type_of_work[ready_row[0]][ready_row[1]] += 1
                else:
                    type_of_work[ready_row[0]][ready_row[1]] = 1 
            else:
                type_of_work[ready_row[0]] = {ready_row[1]: 1}
        type_of_work = self._sorting_by_executor(type_of_work)
        
        return type_of_work

    def prepare_report(self) -> str:
        entries = self._prepare_entries()
        if entries:
            # Словарь вида dict(название работ: list(общее кол-во обращений по виду 
            # работ: сформированный текст отчёта)) для сортировки по убыванию кол-ва
            # обращений по виду работ.
            dict_for_sort = {}

            # Подготавливаем шапку нашего отчёта.
            full_text = report_text['have_appl'].format(BasicTools.get_currenttime(), 
                                                        str(self.total_appl), 
                                                        BasicTools.ending_of_word(self.total_appl)
                                                        )

            # Пробегаем по нашему словарю с видом работ и исполнителями type_of_work, 
            # формируя дополнительные строки отчёта к нашей шапке.
            for type_of_work, executor_list in entries.items():
                total_amount = 0
                text_template = '● {} - <b>{} {}:</b>'

                for executor, amount in executor_list.items():
                    total_amount += amount
                    # Проверка на последнюю запись в списке исполнителей для правильной 
                    # подстановки знака препинания в конце предложения.
                    if executor == list(executor_list.items())[-1][0]:
                        text_template += f'\n{executor} - {amount} {BasicTools.ending_of_word(amount)}.'
                    else:
                        text_template += f'\n{executor} - {amount} {BasicTools.ending_of_word(amount)};'
                # Подставляем значения в наш шаблон (text_template) с присоединёнными 
                #строками об исполнителях. 
                prepare_text = text_template.format(type_of_work, 
                                                    total_amount, 
                                                    BasicTools.ending_of_word(total_amount)
                                                    )
                
                dict_for_sort[type_of_work] = [total_amount, prepare_text]
            
            sorted_dict = self._sorting_by_type_of_work(dict_for_sort)

            # Перебираем наш словарь, отсортированный по убыванию кол-ва обращений.    
            for key in sorted_dict:
                # Соединям шапку отчёта с остальным, подготовленным текстом.
                full_text += f'\n{sorted_dict[key][1]}'
                
            return full_text    
        
        else:
            return report_text['not_appl'].format(BasicTools.get_currenttime())