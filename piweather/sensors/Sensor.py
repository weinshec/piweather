import time


class Sensor(object):

    dtypes = {}

    def __init__(self, cache=0):
        self._cache = cache
        self._last_query = 0
        self._last_value = 0
        if self.dtypes == {}:
            raise NotImplementedError(
                "Must specify dtypes for {}".format(type(self)))

    @property
    def value(self):
        if self._cache_expired():
            new_values = self.read()
            self._check_dtype_consistency(new_values)
            self._last_value = new_values
            self._last_query = time.monotonic()
        return self._last_value

    def read(self):
        raise NotImplementedError("Override this method!")

    def _cache_expired(self):
        return time.monotonic() - self._last_query > self._cache

    def _check_dtype_consistency(self, new_values):
        for key, type_ in self.dtypes.items():
            if key not in new_values:
                raise KeyError("{} must fill value for '{}'".format(
                    type(self), key
                ))
            if type(new_values[key]) != type_:
                raise TypeError(
                    "'{}' of {} assumed to be of type {}, but is {}".format(
                        key, type(self), type_, type(new_values[key])
                    )
                )
