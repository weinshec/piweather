import time
import unittest

from piweather import sensors


class TestSensor(unittest.TestCase):

    def test_Sensor_value_raises_exception_if_not_child_class(self):
        s = sensors.Sensor()
        with self.assertRaises(NotImplementedError):
            s.value

    def test_Sensor_has_value_property(self):
        s = sensors.Dummy()
        self.assertIsNotNone(s.value)
        self.assertNotEquals(s.value, 0)

    def test_Sensor_can_cache_time_for_value(self):
        s = sensors.Dummy(cache=0.1)
        val = s.value
        self.assertEqual(val, s.value)
        time.sleep(0.2)
        self.assertNotEquals(val, s.value)
