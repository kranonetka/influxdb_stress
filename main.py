from stress_tester import StressTester
import json
from datetime import datetime, timedelta

sensors = dict(
    float_sensors=10,
    int_sensors=0,
    str_sensors=0,
    bool_sensors=0
)

if __name__ == '__main__':
    with open('config.json', 'r') as fp:
        config = json.load(fp)

    tester = StressTester(**config)
    tester.drop_db()
    print(f'На удаление БД затрачено {tester.time_diff:.2f} сек.')

    tester.create_db()
    print(f'На создание БД затрачено {tester.time_diff:.2f} сек.')

    tester.write(
        nodes_count=1,
        duration=60 * 5,
        **sensors,
        start_date=datetime(2020, 1, 1)
    )
    print(f'На запись затрачено {tester.time_diff:.2f} сек.')

    _, resp = tester.read(
        5,
        start_date=datetime(2020, 1, 1),
        end_date=datetime(2020, 1, 1) + timedelta(minutes=5),
        time_interval='1s'
    )
    print(f'На чтение затрачено {tester.time_diff:.2f} сек.')
    print(f'Результат выборки: {resp}')
