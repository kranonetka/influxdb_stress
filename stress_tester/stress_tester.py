import requests
import time
from threading import Barrier, Thread, current_thread
from datetime import datetime
import random
import string
from itertools import chain
from contextlib import contextmanager


class StressTester:
    def __init__(self, host, port=8086, db='stress', precision='ms', headers=None):
        self._influxdb_url = f'http://{host}:{port}'

        self._ping_endpoint = self._influxdb_url + '/ping'

        self._write_endpoint = self._influxdb_url + '/write'
        self._write_params = dict(db=db, precision=precision)

        self._query_endpoint = self._influxdb_url + '/query'
        self._create_db_params = dict(q=f'CREATE DATABASE "{db}"')
        self._drop_db_params = dict(q=f'DROP DATABASE "{db}"')
        self._read_params = dict(epoch=precision)

        if precision == 'ms':
            self._second_multiplier = 1000
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
    def random_float(self) -> str:
        """
        :return: Случайное вещественное число из диапазона [0;1000) для записи в InfluxDB
        """
        return '{:.5e}'.format(random.random() * 1000)

    @property
    def random_int(self) -> str:
        """
        :return: Случайное целое число из диапазона [0; 10000) для записи в InfluxDB
        """
        return f'{random.randrange(1000)}i'

    @property
    def random_str(self) -> str:
        """
        :return: Случайная строка длина 60 для записи в InfluxDB
        """
        return '"{}"'.format(''.join(random.choices(string.ascii_letters, k=60)))

    @property
    def random_bool(self) -> str:
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
        """
        if start_date is None:
            start_date = datetime.now()

        start_writing = Barrier(nodes_count, action=self._set_start_time)
        end_writing = Barrier(nodes_count, action=self._set_end_time)

        start_timestamp_ms = int(start_date.timestamp() * self._second_multiplier)

        def _thread_func():
            dot_template = 'python_measurement,thread={} {{{{}}}}={{{{}}}},q=0 {{}}'.format(current_thread().name)

            payload = '\n'.join(
                '\n'.join(
                    chain(
                        (time_template.format('float', self.random_float) for _ in range(float_sensors)),
                        (time_template.format('int', self.random_int) for _ in range(int_sensors)),
                        (time_template.format('str', self.random_str) for _ in range(str_sensors)),
                        (time_template.format('bool', self.random_bool) for _ in range(bool_sensors)),
                    )
                )
                for time_template in map(
                    dot_template.format,
                    map(
                        start_timestamp_ms.__add__,
                        map(
                                self._second_multiplier.__mul__,
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

        self.create_db()
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        return self.time_diff

    def read(self):
        """q=SELECT mean("v") FROM "autogen"."ogamma_measurement"
        WHERE ("n" = 'Temperature') AND time >= now() - 5m
        GROUP BY time(200ms) fill(none)"""
        raise NotImplementedError("Чтение не реализовано")
