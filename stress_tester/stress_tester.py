from typing import Union, Tuple

import requests
import time
from threading import Barrier, Thread, current_thread
from datetime import datetime
import random
import string
from itertools import chain
from contextlib import contextmanager
from functools import partial
from operator import mul


class StressTester:
    def __init__(self, host, port=8086, db='stress', precision='ms', headers=None):
        self._influxdb_url = f'http://{host}:{port}'

        self._ping_endpoint = self._influxdb_url + '/ping'

        self._write_endpoint = self._influxdb_url + '/write'
        self._write_params = dict(db=db, precision=precision)

        self._query_endpoint = self._influxdb_url + '/query'
        self._create_db_params = dict(q=f'CREATE DATABASE "{db}"')
        self._drop_db_params = dict(q=f'DROP DATABASE "{db}"')
        self._default_read_params = dict(db=db, epoch=precision)

        if precision == 'ms':
            self._second_multiplier = partial(mul, 1000)
        else:
            raise NotImplementedError('Не реализована точность, отличная от ms')

        if headers is None:
            self._headers = {}
        else:
            self._headers = headers

        self._start_time = None
        self._end_time = None

        self.ping()

    def _set_start_time(self):
        """
        Служебный метод для того, чтобы засечь время начала операции над InfluxDB
        """
        self._start_time = time.time()

    def _set_end_time(self):
        """
        Служебный метод для того, чтобы засечь время конца операции над InfluxDB
        """
        self._end_time = time.time()

    @contextmanager
    def _timeit(self):
        """
        Служебный контекстный менеджер для засекания времени выполнения однопоточных операций
        """
        try:
            self._set_start_time()
            yield
            self._set_end_time()
        finally:
            pass

    @property
    def time_diff(self):
        """
        :return: Разница (в секундах), затраченная на выполнение последней операции над InfluxDB
        """
        return self._end_time - self._start_time

    @property
    def _random_float(self) -> str:
        """
        :return: Случайное вещественное число из диапазона [0;1000) для записи в InfluxDB
        """
        return '{:.5e}'.format(random.random() * 1000)

    @property
    def _random_int(self) -> str:
        """
        :return: Случайное целое число из диапазона [0; 10000) для записи в InfluxDB
        """
        return f'{random.randrange(1000)}i'

    @property
    def _random_str(self) -> str:
        """
        :return: Случайная строка длина 60 для записи в InfluxDB
        """
        return '"{}"'.format(''.join(random.choices(string.ascii_letters, k=60)))

    @property
    def _random_bool(self) -> str:
        """
        :return: Случайное булево значение для записи в InfluxDB
        """
        return random.choice('tf')

    def ping(self):
        """
        Проверка доступности InfluxDB
        """
        with self._timeit():
            requests.get(self._ping_endpoint, headers=self._headers).raise_for_status()

    def create_db(self):
        """
        Создание БД
        """
        with self._timeit():
            requests.post(self._query_endpoint, params=self._create_db_params, headers=self._headers)

    def drop_db(self):
        """
        Удаление БД
        """
        with self._timeit():
            requests.post(self._query_endpoint, params=self._drop_db_params, headers=self._headers)

    def write(self,
              nodes_count: int,
              float_sensors: int = 1,
              int_sensors: int = 1,
              str_sensors: int = 1,
              bool_sensors: int = 1,
              duration: int = 1,
              start_date: datetime = None) -> float:
        """
        Одновременная запись несколькими потоками

        :param nodes_count: Количество одновременно пишущих узлов (потоков)
        :param float_sensors: Количество вещественных датчиков на узле
        :param int_sensors: Количество целочисленных датчиков на узле
        :param str_sensors: Количество строковых датчиков на узле
        :param bool_sensors: Количество булевых датчиков на узле
        :param duration: На протяжении скольки секунд копились данные для записи каждым узлом
        :param start_date: Начиная с какой даты вести запись. По умолчанию - локальная дата запуска метода
        :return: Время (в секундах), прошедшее с момента одновременного начала отправки данных каждым потоком
            до момента получения ответа каждым из потоков

        Примечание: Каждый поток подготавливает и держит свои данные для отправик в памяти. При генерации больших объмов
        будет много времени затрачнго на саму генерацию и много памяти будет отведено под хранение, пока остальные
        потоки не сгенерируют свои данные
        """
        if start_date is None:
            start_date = datetime.now()

        start_writing = Barrier(nodes_count, action=self._set_start_time)
        end_writing = Barrier(nodes_count, action=self._set_end_time)

        start_timestamp_ms = int(self._second_multiplier(start_date.timestamp()))

        def _thread_func():
            dot_template = 'python_measurement,thread={} {{{{}}}}={{{{}}}},q=0 {{}}'.format(current_thread().name)

            payload = '\n'.join(
                '\n'.join(
                    chain(
                        (time_template.format('float', self._random_float) for _ in range(float_sensors)),
                        (time_template.format('int', self._random_int) for _ in range(int_sensors)),
                        (time_template.format('str', self._random_str) for _ in range(str_sensors)),
                        (time_template.format('bool', self._random_bool) for _ in range(bool_sensors)),
                    )
                )
                for time_template in map(
                    dot_template.format,
                    map(
                        start_timestamp_ms.__add__,
                        map(
                                self._second_multiplier,
                                range(duration)
                            )
                        )
                    )
                ).encode()

            start_writing.wait()
            requests.post(self._write_endpoint, params=self._write_params, data=payload, headers=self._headers)
            end_writing.wait()

        nodes_count_digits = len(str(nodes_count))
        name_string = f'{{:0>{nodes_count_digits}}}'
        threads = [Thread(target=_thread_func, name=name_string.format(i+1)) for i in range(nodes_count)]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        return self.time_diff

    def read(self,
             nodes_count: int,
             aggregation: str = 'mean',
             type: str = 'float',
             start_date: Union[datetime, str] = 'now() - 5m',
             end_date: Union[datetime, str] = 'now()',
             time_interval: str = '5s') -> Tuple[float, dict]:
        """
        Одновременное чтение несколькими потоками

        :param nodes_count: Количество одновременно читающих узлов (потоков)
        :param aggregation: Функция агрегации, применяемая к группам. По умолчанию mean
        :param type: Тип читаемых значений. По умолчанию float
        :param start_date: Начало временного окна. Задаётся в виде datetime объекта,
            либо строкой по правилам синтаксиса InfluxDB
            (см. https://docs.influxdata.com/influxdb/v1.8/query_language/explore-data/#time-syntax)
        :param end_date: Конец временного окна. Задаётся в виде datetime объекта,
            либо строкой по правилам синтаксиса InfluxDB
            (см. https://docs.influxdata.com/influxdb/v1.8/query_language/explore-data/#time-syntax)
        :param time_interval: Временной интервал для группировки. Задаётся строкой по правилам синтаксиса Influxdb
            (см. https://docs.influxdata.com/influxdb/v1.8/query_language/spec/#durations)
        :return: Время (в секундах), прошедшее с момента одновременного начала чтения данных каждым потоком
            до момента получения ответа каждым из потоков и результат выборки

        Примечание: выбираются записи с любыми тегами
        """

        ready_to_read = Barrier(nodes_count, action=self._set_start_time)
        finished_reading = Barrier(nodes_count, action=self._set_end_time)

        if isinstance(start_date, datetime):
            start_date = int(self._second_multiplier(start_date.timestamp()))
            start_date = f'{start_date}ms'

        if isinstance(end_date, datetime):
            end_date = int(self._second_multiplier(end_date.timestamp()))
            end_date = f'{end_date}ms'

        query = f'SELECT {aggregation}("{type}") FROM "autogen"."python_measurement" ' \
                f'WHERE {start_date} <= time AND time <= {end_date} ' \
                f'GROUP BY time({time_interval})'

        params = dict(self._default_read_params, q=query)

        def _thread_func():
            ready_to_read.wait()
            requests.get(self._query_endpoint, params=params, headers=self._headers)
            finished_reading.wait()

        threads = [Thread(target=_thread_func) for _ in range(nodes_count)]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        result = requests.get(self._query_endpoint, params=params, headers=self._headers).json()

        return self.time_diff, result
