from stress_tester import StressTester
import json

sensors = dict(
    float_sensors=0,
    int_sensors=1,
    str_sensors=0,
    bool_sensors=0
)

if __name__ == '__main__':
    with open('config.json', 'r') as fp:
        config = json.load(fp)

    tester = StressTester(**config)
    tester.drop_db()
    print(f'На удаление БД затрачено {tester.time_diff:.2f} сек.')

    tester.write(nodes_count=10**6, duration=1, **sensors)
    print(f'На запись затрачено {tester.time_diff:.2f} сек.')
