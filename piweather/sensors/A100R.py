import logging
import time

from piweather.sensors import Sensor

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except ImportError:
    logging.warning("Module RPi.gpio not found, maybe you're not on a Raspi")


class A100R(Sensor):

    def __init__(self, pin, R=60, *args, **kwargs):
        super(A100R, self).__init__(*args, **kwargs)
        self._pin = pin
        self._calib = 60/R    # R in rpm/(m/s)
        self._init_gpio()

        self.counts_per_second(reset=True)

    @property
    def pin(self):
        return self._pin

    def read(self):
        return self._calib * self.counts_per_second(reset=True)

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

    def _init_gpio(self):
        try:
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(
                self.pin, GPIO.FALLING, callback=self.counter_callback)
        except NameError:
            logging.warning(
                "Module RPi.gpio not found, maybe you're not on as Raspi")
