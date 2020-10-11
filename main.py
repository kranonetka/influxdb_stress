from menu import get_menu
import json


if __name__ == '__main__':
    with open('influxdb_config.json', 'r') as fp:
        config = json.load(fp)
    menu = get_menu(config)
    menu.call()
