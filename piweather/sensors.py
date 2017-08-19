import logging
import numpy as np
import random
import time
try:
    import RPi.GPIO as GPIO
except ImportError:
    logging.warning("Module RPi.gpio not found, maybe you're not on as Raspi")


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


class Dummy(Sensor):

    def read(self):
        return random.random()


class DS18x20(Sensor):

    def __init__(self, path, *args, **kwargs):
        super(DS18x20, self).__init__(*args, **kwargs)
        self._path = path

    @property
    def path(self):
        return self._path

    def read(self):
        try:
            logging.debug("DS18x20: opening path: {}".format(self.path))
            with open(self.path, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            logging.error("DS18x20: File not found at {}".format(self.path))
            return np.NaN

        if self._crc_is_invalid(lines):
            logging.warning("DS18x20: invalid CRC")
            return np.NaN

        raw = self._extract_raw_temperature(lines)
        if raw == "85000":
            logging.warning("DS18x20: T=85000 error occured")
            return np.NaN

        return int(raw)/1000

    def _extract_raw_temperature(self, lines):
        last_token = lines[1].split(" ")[-1]
        return last_token[len("t="):]

    def _crc_is_invalid(self, lines):
        return "YES" not in lines[0]


class A100R(Sensor):

    def __init__(self, pin, *args, **kwargs):
        super(A100R, self).__init__(*args, **kwargs)
        self._pin = pin
        self._counts = 0
        self._init_gpio()

    @property
    def counts(self):
        return self._counts

    @property
    def pin(self):
        return self._pin

    def read(self):
        cts = self.counts
        self._counts = 0
        return cts

    def counter_callback(self):
        self._counts += 1

    def _init_gpio(self):
        try:
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(
                self.pin, GPIO.FALLING, callback=self.counter_callback)
        except NameError:
            logging.warning(
                "Module RPi.gpio not found, maybe you're not on as Raspi")
