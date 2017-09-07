import logging
import numpy as np
import piweather
import time

from piweather.sensors import Sensor

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except ImportError:
    logging.warning("Module RPi.gpio not found, maybe you're not on a Raspi")


class A100R(Sensor):

    # TODO: When object goes out of scope the job and callbacks remain

    dtypes = {
        "windspeed_avg": float,
        "windspeed_std": float,
        "windspeed_min": float,
        "windspeed_max": float,
    }

    def __init__(self, pin, sampling_time=10, R=60, *args, **kwargs):
        super(A100R, self).__init__(*args, **kwargs)
        self._pin = pin
        self._calib = 60/R    # R in rpm/(m/s)
        self._init_gpio()
        self._reset_statistics()
        self.counts_per_second(reset=True)

        self._job = piweather.scheduler.add_job(
            self.sample, "interval", seconds=sampling_time)

    @property
    def pin(self):
        return self._pin

    @property
    def avg(self):
        if self._nSamples == 0:
            return 0.
        return self._calib * self._sum / self._nSamples

    @property
    def std(self):
        if self._nSamples <= 1:
            return 0.
        return self._calib * float(
            np.sqrt(
                (self._sum2 - self._sum*self._sum / self._nSamples)
                / (self._nSamples - 1)
            )
        )

    @property
    def min(self):
        return self._calib * self._min

    @property
    def max(self):
        return self._calib * self._max

    def read(self):
        data = {
            "windspeed_avg": self.avg,
            "windspeed_std": self.std,
            "windspeed_min": self.min,
            "windspeed_max": self.max,
        }
        self._reset_statistics()
        return data

    def counts_per_second(self, reset=True):
        now = time.time()
        seconds = now - getattr(self, "_start_time", 0)
        counts = getattr(self, "_counts", 0)

        if reset:
            self._start_time = now
            self._counts = 0

        return counts / seconds

    def counter_callback(self, channel):
        self._counts += 1

    def sample(self):
        cps = self.counts_per_second(reset=True)

        if self._nSamples == 0 or self._min > cps:
            self._min = cps
        if self._nSamples == 0 or self._max < cps:
            self._max = cps

        self._sum += cps
        self._sum2 += cps*cps
        self._nSamples += 1

    def _init_gpio(self):
        try:
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(
                self.pin, GPIO.FALLING, callback=self.counter_callback)
        except NameError:
            logging.warning(
                "Module RPi.gpio not found, maybe you're not on as Raspi")

    def _reset_statistics(self):
        self._nSamples = 0
        self._sum = 0
        self._sum2 = 0
        self._min = 0
        self._max = 0
