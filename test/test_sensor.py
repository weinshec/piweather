import numpy as np
import os
import time
import unittest

from piweather import sensors
from tempfile import NamedTemporaryFile


class TestSensor(unittest.TestCase):

    def test_Sensor_value_raises_exception_if_not_child_class(self):
        s = sensors.Sensor()
        with self.assertRaises(NotImplementedError):
            s.value

    def test_Sensor_has_value_property(self):
        s = sensors.Dummy()
        self.assertIsNotNone(s.value)
        self.assertNotEqual(s.value, 0)

    def test_Sensor_can_cache_time_for_value(self):
        s = sensors.Dummy(cache=0.1)
        val = s.value
        self.assertEqual(val, s.value)
        time.sleep(0.2)
        self.assertNotEqual(val, s.value)


class TestDS18x20(unittest.TestCase):

    valid = (b"2d 00 4b 46 ff ff 03 10 dd : crc=dd YES\n"
             b"2d 00 4b 46 ff ff 03 10 dd t=22562")

    invalid = (b"2d 00 4b 46 ff ff 03 10 dd : crc=fa NO\n"
               b"2d 00 4b 46 ff ff 03 10 dd t=22562")

    t85000 = (b"2d 00 4b 46 ff ff 03 10 dd : crc=dd YES\n"
              b"2d 00 4b 46 ff ff 03 10 dd t=85000")

    def test_correctly_parses_temperature_from_file(self):
        try:
            with NamedTemporaryFile(delete=False) as valid_file:
                valid_file.write(self.valid)
            s = sensors.DS18x20(valid_file.name)
            self.assertEqual(s.value, 22.562)
        finally:
            os.remove(valid_file.name)

    def test_returns_NaN_if_crc_is_invalid(self):
        try:
            with NamedTemporaryFile(delete=False) as invalid_crc:
                invalid_crc.write(self.invalid)
            s = sensors.DS18x20(invalid_crc.name)
            np.testing.assert_equal(s.value, np.NaN)
        finally:
            os.remove(invalid_crc.name)

    def test_returns_NaN_if_T85000(self):
        try:
            with NamedTemporaryFile(delete=False) as t85000:
                t85000.write(self.t85000)
            s = sensors.DS18x20(t85000.name)
            np.testing.assert_equal(s.value, np.NaN)
        finally:
            os.remove(t85000.name)

    def test_returns_NaN_file_is_not_readable(self):
        s = sensors.DS18x20("/tmp/nonexisting.file")
        np.testing.assert_equal(s.value, np.NaN)


class TestA100R(unittest.TestCase):

    def test_has_pin_attribute(self):
        s = sensors.A100R(pin=18)
        self.assertEqual(s.pin, 18)

    def test_gpio_callback_increases_counts(self):
        s = sensors.A100R(pin=18)
        self.assertEqual(s.counts, 0)
        s.counter_callback()
        s.counter_callback()
        self.assertEqual(s.counts, 2)

    def test_retrieving_value_resets_counter(self):
        s = sensors.A100R(pin=18)
        self.assertEqual(s.value, 0)
        s.counter_callback()
        self.assertGreater(s.value, 0)
        self.assertEqual(s.value, 0)
