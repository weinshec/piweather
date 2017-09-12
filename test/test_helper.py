import piweather
import unittest

from piweather.helper import load_external, get_viewport


class TestExternalLoading(unittest.TestCase):

    def test_load_config_given_file(self):
        config = load_external("test/static/config.py")
        self.assertIn("piweather", config.TITLE)

    def test_load_config_fails_if_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            load_external("foobar")


class TestViewport(unittest.TestCase):

    def test_gets_viewport_from_config_file(self):
        piweather.config = load_external("test/static/config.py")
        self.assertIsNotNone(get_viewport())
        piweather.config = None

    def test_gets_viewport_even_if_not_set(self):
        self.assertIsNotNone(get_viewport())
