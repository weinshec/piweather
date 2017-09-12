import logging
import numpy as np
import piweather
from datetime import datetime
from piweather.database import get_engine, map_dtype
from sqlalchemy import MetaData, Table, Column, sql


class Measurement(object):

    def __init__(self, sensor, table, frequency=0):
        self._sensor = sensor
        self._table = table
        self.frequency = frequency

        self._init_db_table()

    @property
    def frequency(self):
        if hasattr(self, "_job"):
            return self._job.trigger.interval.seconds
        else:
            return 0

    @frequency.setter
    def frequency(self, f):
        job = getattr(self, "_job", None)

        if f > 0:
            if job is None:
                self._job = piweather.scheduler.add_job(
                    self.acquire, "interval", seconds=f)
            else:
                self._job.reschedule("interval", seconds=f)
        else:
            if job is None:
                return
            else:
                self._job.remove()
                self._job = None

    @property
    def last(self):
        return getattr(self, "_last", {})

    @last.setter
    def last(self, values):
        self._last = dict(time=datetime.now())
        self._last.update(values)

    @property
    def table(self):
        return self._table

    @property
    def columns(self):
        return self.sensor.dtypes.keys()

    @property
    def sensor(self):
        return self._sensor

    def acquire(self):
        self.last = self.sensor.value

        with get_engine().connect() as con:
            table = Table(self.table, MetaData(get_engine()), autoload=True)
            insert = table.insert().values(**self.last)
            con.execute(insert)

    def data(self, columns=None, since=None):
        with get_engine().connect() as con:
            table = Table(self.table, MetaData(get_engine()), autoload=True)

            if columns is None:
                stm = sql.select([table])
            elif type(columns) == str:
                stm = sql.select([table.c[columns]])
            elif type(columns) == list:
                stm = sql.select([table.c[col] for col in columns])

            if since is not None:
                stm.append_whereclause(table.c.time > since)

            rs = con.execute(stm)

            matrix = np.array(rs.fetchall())
            if matrix.shape == (0,):
                return {col: [] for col in rs.keys()}
            else:
                return {col: matrix[:, i] for i, col in enumerate(rs.keys())}

    def _init_db_table(self):
        logging.debug("create table '{}' if not exists".format(self.table))

        with get_engine().connect():
            columns = [Column("time", map_dtype(datetime))]
            for name, type_ in self.sensor.dtypes.items():
                columns.append(Column(name, map_dtype(type_)))

            table = Table(self.table, MetaData(get_engine()), *columns)
            table.create(checkfirst=True)
