InfluxDB Stress Test
====================

Инструмент для нагрузочного тестирования СУБД временных рядов InfluxDB

.. contents:: Содержание:
   :backlinks: top
   :local:

Инициализация окружения
-----------------------

Инструмент написан с использованием ЯП `Python 3.8 <https://www.python.org/downloads/>`_
и инструмента для работы с виртуальным окружением Python `pipenv <https://pipenv-fork.readthedocs.io/en/latest/>`_

.. code:: sh

    pip install pipenv

Чтобы начать работать с инструментом, необходимо инициализировать виртуальное окружение

.. code:: sh

    pipenv install

И активировать его

.. code:: sh

    pipenv shell

Документация
------------

Для репозитория настроено автоматическое обновление документации. Самая свежая документация находится по адресу https://kranonetka.github.io/influxdb_stress/

Локальная тестовая среда
------------------------

Репозиторий содержит ``docker-compose.yml`` для развёртывания тестовой среды из:

    - `InfluxDB <https://www.influxdata.com/products/influxdb-overview/>`_ - целевая СУБД ВР для тестирования
    - `ogamma Visual Logger for OPC <https://www.onewayautomation.com/index.php/visual-logger>`_ - инструмент для транслирования данных с OPC UA серверов в СУБД ВР
    - `Grafana <https://grafana.com/>`_ - инструмент для интерактивной визуализации данных

Достаточно выполнить развёртывание окружения

.. code:: sh

    docker-compose up --build

После чего ``InfluxDB`` сразу готова к работе. По желанию можно сконфигурировать
``ogamma Visual Logger for OPC`` и ``Grafana`` для использования с ``InfluxDB``.

Порты сервисов:

    - ``InfluxDB`` доступна на порту 8090
    - ``ogamma Visual Logger for OPC`` - 8091
    - ``Grafana`` - 8092

Сервисы ``ogamma Visual Logger for OPC`` и ``Grafana`` видят ``InfluxDB`` по адресу ``influxdb``.
