import requests
import time
import tqdm
from datetime import datetime, timedelta
import random
from threading import Barrier, Thread, Event, current_thread
from datetime import datetime


class StressTester:
    def ping(self):
        requests.get(f'{self._influxdb_url}/ping', headers=self._headers).raise_for_status()

    def __init__(self, host, port=8086, headers=None):
        self._influxdb_url = f'http://{host}:{port}'

        if headers is None:
            self._headers = {}
        else:
            self._headers = headers

        self._start_time = None
        self._end_time = None

        self.ping()

    def _set_start_time(self):
        self._start_time = time.time()

    def _set_end_time(self):
        self._end_time = time.time()

    @property
    def time_diff(self):
        return self._end_time - self._start_time

    def write(self, nodes_count, float_sensors=1, int_sensors=1, str_sensors=1, bool_sensors=1, iterations=1):
        start_writing = Barrier(nodes_count, action=self._set_start_time)
        end_writing = Barrier(nodes_count, action=self._set_end_time)

        start_timestamp_mcs = int(datetime.now().timestamp() * 1000)

        def _thread_func():
            dot_template = f'python_measurement,thread={current_thread().name} v={{v}},q=0i {{timestamp}}'

            payload = bytearray()
            for it in range(iterations):
                for f in range(float_sensors):
                    ...
                for i in range(int_sensors):
                    ...
                for s in range(str_sensors):
                    ...
                for b in range(bool_sensors):
                    ...

            start_writing.wait()
            end_writing.wait()

        nodes_count_digits = len(str(nodes_count))
        name_string = f'{{:0>{nodes_count_digits}}}'
        threads = [Thread(target=_thread_func, name=name_string.format(i+1)) for i in range(nodes_count)]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        print(self.time_diff, "sec")
