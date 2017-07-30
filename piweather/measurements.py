import piweather
from pandas import DataFrame, Timestamp


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

    def acquire(self):
        raise NotImplementedError("Override this method!")

    def _store(self, df):
        df.to_sql(self._table, piweather.db, if_exists='append', index=False)


class Single(Measurement):

    def acquire(self):
        val = self._sensor.value
        data = DataFrame({'time': Timestamp.now(), 'value': val}, index=[0])
        self._store(data)
