from stress_tester import StressTester
import json

if __name__ == '__main__':
    with open('config.json', 'r') as fp:
        config = json.load(fp)

    tester = StressTester(**config)
    tester.drop_db()
    result = tester.write(nodes_count=1, duration=60 * 24)
    print(f'{result:.2f} sec')
