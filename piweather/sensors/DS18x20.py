import logging
import numpy as np
from piweather.sensors import Sensor


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
        return last_token[len("t="):].strip()

    def _crc_is_invalid(self, lines):
        return "YES" not in lines[0]
