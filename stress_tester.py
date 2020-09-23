import requests
from datetime import datetime, timedelta
import random
from threading import Barrier, Thread, Event


class StressTester:
    def __init__(self, host, port=8086):
        self._influx_url = f"http://{host}:{port}"

    def write(self, nodes_count):
        pass