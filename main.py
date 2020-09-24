from stress_tester import StressTester
import json

if __name__ == '__main__':
    with open('config.json', 'r') as fp:
        config = json.load(fp)

    tester = StressTester(**config)
    tester.write(100)
