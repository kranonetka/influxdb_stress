import json
from pathlib import Path

from menu import get_menu


def main():
    with (Path(__file__).parent / 'influxdb_config.json').open(mode='r') as fp:
        config = json.load(fp)
    menu = get_menu(config)
    menu.call()


if __name__ == '__main__':
    main()
