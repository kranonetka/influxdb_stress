import sys
from abc import ABC
from datetime import datetime
import re

from console_menu import MenuLayer, MenuEntry
from stress_tester import StressTester


def _parse_date(date_str: str):
    regex = re.compile(r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})'
                       r'(?: (?P<hour>\d{2})(?::(?P<minute>\d{2})(?::(?P<second>\d{2}))?)?)?')
    
    params = regex.match(date_str)
    
    if not params:
        raise ValueError('Неправильный формат даты. Ожидаемый: YYYY.MM.DD HH:MM:SS')
    
    params = params.groupdict(default='0')
    params = {key: int(value) for key, value in params.items()}
    
    return datetime(**params)


class DefaultMenu(MenuLayer, ABC):
    def call(self):
        while True:
            super().call()
            key = input('Ввод: ')
            try:
                entry = self._entries[int(key) - 1]
            except:
                pass
            else:
                break
        entry.call()


def _get_write_menu():
    class WriteMenu(DefaultMenu):
        name = 'Оценка скорости записи'
        
        __slots__ = ('nodes_count', 'float_sensors', 'int_sensors', 'str_sensors', 'bool_sensors', 'duration')
        
        def __init__(self):
            super(WriteMenu, self).__init__()
            self.nodes_count: int = 1
            self.float_sensors: int = 1
            self.int_sensors: int = 1
            self.str_sensors: int = 1
            self.bool_sensors: int = 1
            self.duration: int = 1
            self.start_date: datetime = None
    
    write_menu = WriteMenu()
    
    class WriteParamIntEntry(MenuEntry):
        def __init__(self, param: str, prompt_template: str):
            self._prompt_template = prompt_template
            
            def action():
                while True:
                    try:
                        value = int(input('Новое значение: '))
                    except:
                        pass
                    else:
                        break
                setattr(write_menu, param, value)
                self._prompt = self._prompt_template.format(value)
                write_menu.call()
                
            super().__init__(prompt=self._prompt_template.format(getattr(write_menu, param)), action=action)

    class WriteParamDatetimeEntry(MenuEntry):
        def __init__(self, param: str, prompt_template: str):
            self._prompt_template = prompt_template
        
            def action():
                while True:
                    try:
                        value = _parse_date(input('Новое значение (YYYY-MM-DD[ HH[:MM[:SS]]]): '))
                    except:
                        pass
                    else:
                        break
                setattr(write_menu, param, value)
                self._prompt = self._prompt_template.format(value)
                write_menu.call()
        
            super().__init__(prompt=self._prompt_template.format(getattr(write_menu, param)), action=action)
    
    nodes_count_entry = WriteParamIntEntry('nodes_count', 'Количество одновременно пишущих узлов ({})')
    
    float_sensors_entry = WriteParamIntEntry('float_sensors', 'Количество вещественных датчиков на узле ({})')
    int_sensors_entry = WriteParamIntEntry('int_sensors', 'Количество целочисленных датчиков на узле ({})')
    str_sensors_entry = WriteParamIntEntry('str_sensors', 'Количество строковых датчиков на узле ({})')
    bool_sensors_entry = WriteParamIntEntry('bool_sensors', 'Количество булевых датчиков на узле ({})')
    duration_entry = WriteParamIntEntry('duration',
                                        'На протяжении скольки секунд копились данные для записи каждым узлом ({} сек)')
    start_date_entry = WriteParamDatetimeEntry('start_date',
                                               'Начиная с какой даты вести запись (None - с текущего момента) ({})')

    for entry in (nodes_count_entry, float_sensors_entry, int_sensors_entry, str_sensors_entry,
                  bool_sensors_entry, duration_entry, start_date_entry):
        write_menu.add_entry(entry)
    
    return write_menu  # type: WriteMenu

"""
nodes_count: int,
aggregation: str = 'mean',
type: str = 'float',
start_date: Union[datetime, str] = 'now() - 5m',
end_date: Union[datetime, str] = 'now()',
time_interval: str = '5s') -> Tuple[float, dict]:
"""

def _get_read_menu():
    class ReadMenu(DefaultMenu):
        name = 'Оценка скорости чтения'
        
        __slots__ = ('nodes_count', 'aggregation', 'type', 'start_date', 'end_date', 'time_interval')
        
        def __init__(self):
            super(ReadMenu, self).__init__()
            self.nodes_count: int = 1
            self.aggregation: str = 'mean'
            self.type: str = 'float'
            self.start_date: str = 'now() - 5m'
            self.end_date: str = 'now()'
            self.time_interval: str = '5s'
        
    read_menu = ReadMenu()

    class ReadParamIntEntry(MenuEntry):
        def __init__(self, param: str, prompt_template: str):
            self._prompt_template = prompt_template
        
            def action():
                while True:
                    try:
                        value = int(input('Новое значение: '))
                    except:
                        pass
                    else:
                        break
                setattr(read_menu, param, value)
                self._prompt = self._prompt_template.format(value)
                read_menu.call()
        
            super().__init__(prompt=self._prompt_template.format(getattr(read_menu, param)), action=action)

    class ReadParamStrEntry(MenuEntry):
        def __init__(self, param: str, prompt_template: str):
            self._prompt_template = prompt_template
        
            def action():
                while True:
                    try:
                        value = input('Новое значение: ')
                    except:
                        pass
                    else:
                        break
                setattr(read_menu, param, value)
                self._prompt = self._prompt_template.format(value)
                read_menu.call()
        
            super().__init__(prompt=self._prompt_template.format(getattr(read_menu, param)), action=action)

    nodes_count_entry = ReadParamIntEntry('nodes_count', 'Количество одновременно читающих узлов ({})')

    aggregation_entry = ReadParamStrEntry('aggregation', 'Функция агрегации ({})')
    type_entry = ReadParamStrEntry('type', 'Тип читаемых значений ({})')
    start_date_entry = ReadParamStrEntry('start_date', 'Начало временного окна ({})')
    end_date_entry = ReadParamStrEntry('end_date', 'Конец временного окна ({})')
    time_interval_entry = ReadParamStrEntry('time_interval', 'Временной интервал для группировки ({})')
    
    for entry in (nodes_count_entry, aggregation_entry, type_entry,
                  start_date_entry, end_date_entry, time_interval_entry):
        read_menu.add_entry(entry)
        
    return read_menu  # type: ReadMenu


def get_menu(influxdb_config: dict):
    tester = StressTester(**influxdb_config)
    
    class MainMenu(DefaultMenu):
        name = 'Главное меню'

    main_menu = MainMenu()
    main_menu_caller = MenuEntry(main_menu.name, main_menu.call)
    
    read_menu = _get_read_menu()
    
    def read_action():
        try:
            tester.read(
                nodes_count=read_menu.nodes_count,
                aggregation=read_menu.aggregation,
                type=read_menu.type,
                start_date=read_menu.start_date,
                end_date=read_menu.end_date,
                time_interval=read_menu.time_interval
            )
        except Exception as ex:
            print(f'Не удалось выполнить чтение: {ex}')
        else:
            print(f'Время чтения: {tester.time_diff:.2f} сек.')

        input('Нажмите Enter, чтобы продолжить')
        read_menu.call()
    read_menu.add_entry(MenuEntry('Запуск', read_action))
    
    read_menu.add_entry(main_menu_caller)
    read_menu_caller = MenuEntry(read_menu.name, read_menu.call)
    
    write_menu = _get_write_menu()
    
    def write_action():
        try:
            tester.write(
                nodes_count=write_menu.nodes_count,
                float_sensors=write_menu.float_sensors,
                int_sensors=write_menu.int_sensors,
                str_sensors=write_menu.str_sensors,
                bool_sensors=write_menu.bool_sensors,
                duration=write_menu.duration,
                start_date=write_menu.start_date
            )
        except Exception as ex:
            print(f'Не удалось выполнить запись: {ex}')
        else:
            print(f'Время записи: {tester.time_diff:.2f} сек.')
        input('Нажмите Enter, чтобы продолжить')
        write_menu.call()
    write_menu.add_entry(MenuEntry('Запуск', write_action))
    write_menu.add_entry(main_menu_caller)
    write_menu_caller = MenuEntry(write_menu.name, write_menu.call)
    
    exit_entry = MenuEntry('Выход', sys.exit)

    def ping_action():
        try:
            tester.ping()
        except Exception as ex:
            print(f'СУБД недоступна: {ex}')
        else:
            print(f'СУБД доступна. Время ответа {tester.time_diff:.2f} сек.')
        input('Нажмите Enter, чтобы продолжить')
        main_menu.call()
    ping_entry = MenuEntry('Проверить доступность', ping_action)
    
    def create_db_action():
        try:
            tester.create_db()
        except Exception as ex:
            print(f'Не удалось создать БД: {ex}')
        else:
            print(f'БД создана. Время ответа {tester.time_diff:.2f} сек.')
        input('Нажмите Enter, чтобы продолжить')
        main_menu.call()
    create_db_entry = MenuEntry('Создать БД', create_db_action)
    
    def drop_db_action():
        try:
            tester.drop_db()
        except Exception as ex:
            print(f'Не удалось удалить БД: {ex}')
        else:
            print(f'БД удалена. Время ответа {tester.time_diff:.2f} сек.')
        input('Нажмите Enter, чтобы продолжить')
        main_menu.call()
    drop_db_entry = MenuEntry('Удалить БД', drop_db_action)
    
    for entry in (ping_entry, create_db_entry, drop_db_entry, write_menu_caller, read_menu_caller, exit_entry):
        main_menu.add_entry(entry)

    return main_menu
