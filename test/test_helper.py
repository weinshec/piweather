import unittest

from piweather.helper import load_external


class TestExternalLoading(unittest.TestCase):

    def test_load_config_given_file(self):
        config = load_external("test/static/config.py")
        self.assertIn("piweather", config.TITLE)

    def test_load_config_fails_if_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            load_external("foobar")
