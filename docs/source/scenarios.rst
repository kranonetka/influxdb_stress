Примеры реализации некоторых тестовых сценариев
===============================================

.. contents:: Содержание:
   :backlinks: top
   :local:

Реализация сценария пиковой нагрузки
------------------------------------

В качестве пиковой нагрузки понимается ситуация, когда по какой-либо причине СУБД ВР
не получала от OPC UA "регулярные" данные (например, из-за обрыва связи), а потом (после восстановления связи)
происходит всплеск этих данных, и их необходимо быстро записать, чтобы продолжить работать в штатном режиме.

.. code:: python

    from stress_tester import StressTester


    if __name__ == '__main__':
        tester = StressTester(
            host='localhost',
            port='8090'
        )

        tester.drop_db()
        print(f'Удаление БД заняло {tester.time_diff:.2f} сек.')

        tester.create_db()
        print(f'Создание БД заняло {tester.time_diff:.2f} сек.')

        nodes_count = 100
        duration = 60 * 60 * 3

        print(f'Записываем смешанные данные, которые копились с {nodes_count} узлов в течение {duration} сек.')

        delay = tester.write(
            nodes_count=nodes_count,
            float_sensors=1,
            int_sensors=1,
            bool_sensors=1,
            str_sensors=1,
            duration=duration
        )

        print(f'Запись накопившихся за {duration} секунд смешанных данных с {nodes_count} узлов '
              f'заняла {delay:.2f} сек.')


Реализация сценария штатной нагрузки
------------------------------------

Под штатной нагрузкой понимается ситуация, когда работа идёт в штатном режиме. Есть множество технологических
узлов, в каждом узле находится несколько датчиков. Например, ситуация, когда в узое 6 вещественных датчиков и
3 булевых:

.. code:: python

    from stress_tester import StressTester


    if __name__ == '__main__':
        tester = StressTester(
            host='localhost',
            port='8090'
        )

        tester.drop_db()
        print(f'Удаление БД заняло {tester.time_diff:.2f} сек.')

        tester.create_db()
        print(f'Создание БД заняло {tester.time_diff:.2f} сек.')

        nodes_count = 1000
        duration = 1

        print(f'Записываем смешанные данные, которые копились с {nodes_count} узлов в течение {duration} сек.')

        delay = tester.write(
            nodes_count=nodes_count,
            float_sensors=6,
            int_sensors=0,
            bool_sensors=3,
            str_sensors=0,
            duration=duration
        )

        print(f'Запись накопившихся за {duration} секунд смешанных данных с {nodes_count} узлов '
              f'заняла {delay:.2f} сек.')

Реализация сценария запоздавших данных
--------------------------------------

Под завоздавшими данными понимается ситуация, когда по какой-либо причине данные от производства не дошли до
СУБД за ожидаемое время.

.. code:: python

    from stress_tester import StressTester
    from datetime import datetime


    if __name__ == '__main__':
        tester = StressTester(
            host='localhost',
            port='8090'
        )

        tester.drop_db()
        print(f'Удаление БД заняло {tester.time_diff:.2f} сек.')

        tester.create_db()
        print(f'Создание БД заняло {tester.time_diff:.2f} сек.')

        nodes_count = 1000
        duration = 60 * 60

        print(f'Записываем смешанные данные, которые копились с {nodes_count} узлов в течение {duration} сек.')

        delay = tester.write(
            nodes_count=nodes_count,
            float_sensors=6,
            int_sensors=0,
            bool_sensors=3,
            str_sensors=0,
            duration=duration,
            start_date=datetime(
                year=2020,
                month=6,
                day=26,
                hour=19,
                minute=26,
                second=25
            )
        )

        print(f'Запись накопившихся за {duration} секунд смешанных данных с {nodes_count} узлов '
              f'заняла {delay:.2f} сек.')

Реализация сценария получения исторических данных
-------------------------------------------------

Под получением исторических данных подразумевается получение данных за какой-то прошедший период. Но для того,
чтобы эти данные получить, надо, чтобы они сначала там оказались. Данная реализация сценария записывает данные
во временное окно в 5 минут, а затем получает их.

.. code:: python

    from stress_tester import StressTester
    from datetime import datetime, timedelta


    if __name__ == '__main__':
        tester = StressTester(
            host='localhost',
            port='8090'
        )

        tester.drop_db()
        print(f'Удаление БД заняло {tester.time_diff:.2f} сек.')

        tester.create_db()
        print(f'Создание БД заняло {tester.time_diff:.2f} сек.')

        nodes_count = 100
        duration = 60 * 5

        print(f'Записываем смешанные данные, которые копились с {nodes_count} узлов в течение {duration} сек.')

        delay = tester.write(
            nodes_count=nodes_count,
            float_sensors=6,
            int_sensors=0,
            bool_sensors=3,
            str_sensors=0,
            duration=duration,
            start_date=datetime(
                year=2020,
                month=1,
                day=1
            )
        )

        print(f'Запись накопившихся за {duration} секунд смешанных данных с {nodes_count} узлов '
              f'заняла {delay:.2f} сек.')

        delay, response = tester.read(
            nodes_count=1,
            aggregation='sum',
            type='float',
            start_date=datetime(2020, 1, 1),
            end_date=datetime(2020, 1, 1) + timedelta(minutes=5),
            time_interval='5s'
        )

        print(f'Чтение исторических данных с временным окном в 5 минут одним узлом '
              f'заняло {delay:.2f} сек.')

Реализация сценария получения оперативных данных
------------------------------------------------

Под оперативным данными понимаются данные, необходимые для обработки в реальном времени (например, для
визуализации). Чтобы получить оперативные данные, надо, чтобы они в базе были. Данный сценарий симулирует
запись данных в течение 15-ти минут со смещением по времени на 5 минут от текущего, затем получает данные
за последние 5 минут.

.. code:: python

    from stress_tester import StressTester
    from datetime import datetime, timedelta


    if __name__ == '__main__':
        tester = StressTester(
            host='localhost',
            port='8090'
        )

        tester.drop_db()
        print(f'Удаление БД заняло {tester.time_diff:.2f} сек.')

        tester.create_db()
        print(f'Создание БД заняло {tester.time_diff:.2f} сек.')

        nodes_count = 100
        duration = 60 * 15

        print(f'Записываем смешанные данные, которые копились с {nodes_count} узлов в течение {duration} сек.')

        delay = tester.write(
            nodes_count=nodes_count,
            float_sensors=6,
            int_sensors=0,
            bool_sensors=3,
            str_sensors=0,
            duration=duration,
            start_date=datetime.now() - timedelta(minutes=5)
        )

        print(f'Запись накопившихся за {duration} секунд смешанных данных с {nodes_count} узлов '
              f'заняла {delay:.2f} сек.')

        delay, response = tester.read(
            nodes_count=1,
            aggregation='sum',
            type='float',
            time_interval='5s'
        )

        print(f'Чтение оперативных данных за последние 5 минут одним узлом '
              f'заняло {delay:.2f} сек.')
