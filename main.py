import json
from pathlib import Path

from menu import get_menu

if __name__ == '__main__':
    with (Path(__file__).parent / 'influxdb_config.json').open(mode='r') as fp:
        config = json.load(fp)
    menu = get_menu(config)
    menu.call()
