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
