import numpy as np
import pandas as pd
import piweather


class Measurement(object):

    def __init__(self, sensor, table=None, frequency=0):
        self._sensor = sensor
        self._table = table
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

    def acquire(self):
        raise NotImplementedError("Override this method!")

    def _store(self, **kwargs):
        df = pd.DataFrame(
            {key: pd.Series([val], index=[0]) for key, val in kwargs.items()})
        self._last = df
        if self._table is not None:
            df.to_sql(self._table,
                      piweather.db,
                      if_exists='append',
                      index=False)


class Single(Measurement):

    def acquire(self):
        self._store(
            time=pd.Timestamp.now(),
            value=self._sensor.value,
        )


class Statistical(Measurement):

    def __init__(self, sensor, nSamples, *args, **kwargs):
        super(Statistical, self).__init__(sensor, *args, **kwargs)
        self._nSamples = nSamples
        self._data = list()

    def acquire(self):
        self._data.append(self._sensor.value)

        if not self.acquisition_complete():
            return

        self._store(
            time=pd.Timestamp.now(),
            mean=np.mean(self._data),
            std=np.std(self._data),
            min=np.min(self._data),
            max=np.max(self._data),
        )

        self._data = list()

    def acquisition_complete(self):
        return self._nSamples - len(self._data) == 0
