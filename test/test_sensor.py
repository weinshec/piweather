import numpy as np
import os
import piweather
import time
import unittest

from piweather import sensors
from test import TransientDBTestCase
from tempfile import NamedTemporaryFile
from unittest.mock import patch, MagicMock


class TestSensor(unittest.TestCase):

    def test_Sensor_can_cache_time_for_value(self):
        s = sensors.Dummy(cache=0.1)
        val = s.value
        self.assertEqual(val, s.value)
        time.sleep(0.2)
        self.assertNotEqual(val, s.value)

    def test_Sensor_knows_returned_datatypes(self):
        s = sensors.Dummy()
        self.assertIn("random", s.dtypes)
        self.assertEqual(s.dtypes["random"], float)

    def test_Sensor_returns_dictionary_with_correct_types(self):
        s = sensors.Dummy()
        values = s.value
        for k, v in s.dtypes.items():
            self.assertIsInstance(values[k], v)

    @patch("piweather.sensors.Dummy.read")
    def test_Sensor_value_checks_consistency_of_read_dictionary(self, read):

        with self.subTest("Wrong type"):
            s = sensors.Dummy()
            read.return_value = {"random": int(42)}
            with self.assertRaises(TypeError):
                s.value

        with self.subTest("Incomplete"):
            s = sensors.Dummy()
            read.return_value = {}
            with self.assertRaises(KeyError):
                s.value


class TestDS18x20(unittest.TestCase):

    valid = (b"2d 00 4b 46 ff ff 03 10 dd : crc=dd YES\n"
             b"2d 00 4b 46 ff ff 03 10 dd t=22562\n")

    invalid = (b"2d 00 4b 46 ff ff 03 10 dd : crc=fa NO\n"
               b"2d 00 4b 46 ff ff 03 10 dd t=22562\n")

    t85000 = (b"2d 00 4b 46 ff ff 03 10 dd : crc=dd YES\n"
              b"2d 00 4b 46 ff ff 03 10 dd t=85000\n")

    def test_correctly_parses_temperature_from_file(self):
        try:
            with NamedTemporaryFile(delete=False) as valid_file:
                valid_file.write(self.valid)
            s = sensors.DS18x20(valid_file.name)
            self.assertEqual(s.value["temperature"], 22.562)
        finally:
            os.remove(valid_file.name)

    def test_returns_NaN_if_crc_is_invalid(self):
        try:
            with NamedTemporaryFile(delete=False) as invalid_crc:
                invalid_crc.write(self.invalid)
            s = sensors.DS18x20(invalid_crc.name)
            np.testing.assert_equal(s.value["temperature"], np.NaN)
        finally:
            os.remove(invalid_crc.name)

    def test_returns_NaN_if_T85000(self):
        try:
            with NamedTemporaryFile(delete=False) as t85000:
                t85000.write(self.t85000)
            s = sensors.DS18x20(t85000.name)
            np.testing.assert_equal(s.value["temperature"], np.NaN)
        finally:
            os.remove(t85000.name)

    def test_returns_NaN_file_is_not_readable(self):
        s = sensors.DS18x20("/tmp/nonexisting.file")
        np.testing.assert_equal(s.value["temperature"], np.NaN)


class TestA100R(TransientDBTestCase):

    def test_has_pin_attribute(self):
        s = sensors.A100R(pin=18)
        self.assertEqual(s.pin, 18)

    def test_A100R_adds_scheduler_job(self):
        pre = len(piweather.scheduler.get_jobs())
        sensors.A100R(pin=18)
        post = len(piweather.scheduler.get_jobs())

        self.assertEqual(post, pre+1)

    def test_gpio_callback_increases_counts(self):
        s = sensors.A100R(pin=18)
        self.assertEqual(s.counts_per_second(), 0)
        s.counter_callback("channel")
        self.assertGreater(s.counts_per_second(), 0)

    @patch("piweather.sensors.A100R.counts_per_second")
    def test_correctly_sets_min_and_max_values(self, mock_cps):
        s = sensors.A100R(pin=18)

        mock_cps.return_value = 42
        s.sample()
        mock_cps.return_value = 21
        s.sample()
        data = s.value

        self.assertEqual(data["windspeed_min"], 21)
        self.assertEqual(data["windspeed_max"], 42)

    @patch("piweather.sensors.A100R.counts_per_second")
    def test_correctly_updates_runnung_avg_and_std(self, mock_cps):
        s = sensors.A100R(pin=18)

        mock_cps.return_value = 10
        s.sample()
        mock_cps.return_value = 20
        s.sample()
        data = s.value

        self.assertAlmostEqual(
            data["windspeed_avg"], np.mean([10, 20]), delta=0.01)
        self.assertAlmostEqual(
            data["windspeed_std"], np.std([10, 20], ddof=1), delta=0.01)

    def test_retrieving_value_resets_values(self):
        s = sensors.A100R(pin=18)

        s.counter_callback("channel")
        s.sample()

        self.assertGreater(s.value["windspeed_avg"], 0)
        self.assertEqual(s.value["windspeed_avg"], 0)

    @patch("piweather.sensors.A100R.counts_per_second")
    def test_returns_0_if_not_enough_samples(self, mock_cps):
        s = sensors.A100R(pin=18)

        self.assertEqual(s.value["windspeed_avg"], 0)

        mock_cps.return_value = 10
        s.sample()
        self.assertEqual(s.value["windspeed_std"], 0)


smbus = MagicMock()


@patch.dict("sys.modules", smbus=smbus)
class TestBMP280(unittest.TestCase):

    def setUp(self):
        smbus.SMBus().read_i2c_block_data = MagicMock()
        smbus.SMBus().read_byte_data.return_value = 0x00000000

    def test_has_i2c_address(self):
        s = sensors.BMP280()
        self.assertEqual(s.i2c_addr, sensors.BMP280.DEFAULT_I2C_ADDR)

    def test_property_validity_checking(self):
        with self.subTest("osrs_p"):
            s = sensors.BMP280(osrs_p=sensors.BMP280.OSRS["x16"])
            with self.assertRaises(ValueError):
                s.osrs_p = "foobar"

        with self.subTest("osrs_t"):
            s = sensors.BMP280(osrs_t=sensors.BMP280.OSRS["x16"])
            with self.assertRaises(ValueError):
                s.osrs_t = "foobar"

        with self.subTest("filter"):
            s = sensors.BMP280(filtr=sensors.BMP280.FILTER["16"])
            with self.assertRaises(ValueError):
                s.filtr = "foobar"

    def test_ctype_conversions(self):
        s = sensors.BMP280()

        with self.subTest("to short valid"):
            self.assertEqual(s.to_short([0x11, 0x22]), 8721)

        with self.subTest("to unsigned short"):
            self.assertEqual(s.to_ushort([0x11, 0x22]), 8721)

    def test_reads_calibration_values_on_init(self):
        s = sensors.BMP280()
        self.assertIsNotNone(s.calibration)
        self.assertIsNotNone(s.calibration["T1"])

    def test_converts_temperature_correctly(self):
        s = sensors.BMP280()

        # set example calibration from datasheet
        datasheet_calib_example = dict(
            T1=27504, T2=26435, T3=-1000,
            P1=36477, P2=-10685, P3=3024, P4=2855, P5=140, P6=-7, P7=15500,
            P8=-14600, P9=6000,
        )
        s.calibration = datasheet_calib_example

        # mock register content readout
        datasheet_data_example = [0x65, 0x5a, 0xc0, 0x7e, 0xed, 0x00]
        smbus.SMBus().read_i2c_block_data.return_value = datasheet_data_example

        self.assertAlmostEqual(s.value["pressure"], 100653.27, delta=0.01)
