import piweather
import unittest
from piweather.database import get_engine


class TransientDBTestCase(unittest.TestCase):

    def setUp(self):
        piweather.db = get_engine('sqlite:///:memory:')
        if not piweather.scheduler.running:
            piweather.scheduler.start()

    def tearDown(self):
        for job in piweather.scheduler.get_jobs():
            job.remove()
