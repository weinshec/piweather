import logging
import numpy as np
import pandas as pd
import piweather

# TODO: Rename measurment subclasses


class Measurement(object):

    def __init__(self, sensor, table=None, frequency=0, label=None):
        self._sensor = sensor
        self._table = table
        self._label = label
        self.frequency = frequency

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
        return getattr(self, "_last", None)

    @property
    def table(self):
        return getattr(self, "_table", None)

    @property
    def sensor(self):
        return self._sensor

    @property
    def label(self):
        return getattr(self, "_label", "")

    def acquire(self):
        raise NotImplementedError("Override this method!")

    def data(self, since=None):
        if self.table is None:
            logging.warning("No table specified for this measurement!")
            return None

        sql_query = "SELECT * FROM {}".format(self.table)
        if since is not None:
            sql_query += " WHERE time >= '{}'".format(since)
        return pd.read_sql_query(sql_query, piweather.db)

    def _store(self, **kwargs):
        kwargs["time"] = pd.Timestamp.now()
        df = pd.DataFrame(
            {key: pd.Series([val], index=[0]) for key, val in kwargs.items()})
        self._last = df
        if self.table is not None:
            df.to_sql(self.table,
                      piweather.db,
                      if_exists='append',
                      index=False)


class Single(Measurement):

    def acquire(self):
        self._store(value=self.sensor.value)


class Statistical(Measurement):

    def __init__(self, sensor, n, *args, **kwargs):
        super(Statistical, self).__init__(sensor, *args, **kwargs)
        self._n = n
        self._data = list()

    def acquire(self):
        self._data.append(self.sensor.value)

        if not self.acquisition_complete():
            return

        self._store(
            mean=np.mean(self._data),
            std=np.std(self._data),
            min=np.min(self._data),
            max=np.max(self._data),
        )

        self._data = list()

    def acquisition_complete(self):
        return self._n - len(self._data) == 0
