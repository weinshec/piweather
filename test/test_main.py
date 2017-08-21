import piweather
import unittest
from unittest.mock import patch

from piweather.main import load_config, run_loop, run_dash


class TestMainModule(unittest.TestCase):

    def test_load_config(self):
        with self.subTest("loads config from given file"):
            load_config("test/static/config.py")
            self.assertEqual(len(piweather.config.SENSORS), 2)

        with self.subTest("raises exception if file not found"):
            with self.assertRaises(FileNotFoundError):
                load_config("foobar")

    @patch("time.sleep", side_effect=KeyboardInterrupt)
    def test_run_loop(self, mock_sleep):
        with self.subTest("CTRL+C interrupts loop"):
            run_loop()
            self.assertTrue(mock_sleep.called)
