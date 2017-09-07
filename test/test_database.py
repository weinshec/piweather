import unittest
import piweather
import piweather.database as db

from piweather.helper import load_external
from sqlalchemy import Integer, Float


class TestDatabase(unittest.TestCase):

    def setUp(self):
        piweather.db = None
        piweather.config = None

    def tearDown(self):
        piweather.db = None
        piweather.config = None

    def test_can_retrieve_db_engine(self):
        url = "sqlite:///:memory:"
        self.assertIsNone(piweather.db)
        db.get_engine(url)
        self.assertIsNotNone(piweather.db)
        self.assertEqual(str(piweather.db.url), url)

    def test_uses_config_if_url_arg_is_none(self):
        piweather.config = load_external("test/static/config.py")
        db.get_engine()
        self.assertEqual(str(piweather.db.url), piweather.config.DB_ENGINE)

    def test_raises_exception_if_no_url_found(self):
        with self.assertRaises(RuntimeError):
            db.get_engine()

    def test_can_map_python_types_to_SQL_columns(self):
        with self.subTest("valid conversion"):
            self.assertEqual(db.map_dtype(int), Integer)
            self.assertEqual(db.map_dtype(float), Float)

        with self.subTest("unkown type"):
            with self.assertRaises(TypeError):
                db.map_dtype(None)
