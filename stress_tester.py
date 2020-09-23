import requests
from datetime import datetime, timedelta
import random
from threading import Barrier, Thread, Event


class StressTester:
    def ping(self):
        requests.get(f"{self._influx_url}/ping", headers=self._headers).raise_for_status()

    def __init__(self, host, port=8086):
        self._influx_url = f"http://{host}:{port}"
        self._headers = {}

        self.ping()

    def write(self, nodes_count):
        pass