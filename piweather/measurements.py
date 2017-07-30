import numpy as np
import pandas as pd
import piweather


class Measurement(object):

    data_frame = pd.DataFrame()

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

    def acquire(self):
        raise NotImplementedError("Override this method!")

    def _store(self):
        self.data_frame.to_sql(
            self._table, piweather.db, if_exists='append', index=False)


class Single(Measurement):

    data_frame = pd.DataFrame({
        'time':  pd.Series([np.nan], dtype=np.datetime64),
        'value': pd.Series([np.nan], dtype=np.float64),
    }, index=[0])

    def acquire(self):
        self.data_frame.value = self._sensor.value
        self.data_frame.time = pd.Timestamp.now()
        self._store()


class Statistical(Measurement):

    data_frame = pd.DataFrame({
        'time': pd.Series([np.nan], dtype=np.datetime64),
        'mean': pd.Series([np.nan], dtype=np.float64),
        'std':  pd.Series([np.nan], dtype=np.float64),
        'min':  pd.Series([np.nan], dtype=np.float64),
        'max':  pd.Series([np.nan], dtype=np.float64),
    }, index=[0])

    def __init__(self, sensor, nSamples, *args, **kwargs):
        super(Statistical, self).__init__(sensor, *args, **kwargs)
        self._nSamples = nSamples
        self._live_data = list()

    def acquire(self):
        self._live_data.append(self._sensor.value)
        if self.remaining_polls():
            return

        self.data_frame.loc[0, :] = (
            pd.Timestamp.now(),
            np.mean(self._live_data),
            np.std(self._live_data),
            np.min(self._live_data),
            np.max(self._live_data),
        )
        self._store()
        self._live_data = list()

    def remaining_polls(self):
        return self._nSamples - len(self._live_data)
