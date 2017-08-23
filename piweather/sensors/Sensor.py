import time


class Sensor(object):

    def __init__(self, cache=0):
        self._cache = cache
        self._last_query = 0
        self._last_value = 0

    @property
    def value(self):
        if self._cache_expired():
            self._last_value = self.read()
            self._last_query = time.monotonic()
        return self._last_value

    def read(self):
        raise NotImplementedError("Override this method!")

    def _cache_expired(self):
        return time.monotonic() - self._last_query > self._cache
