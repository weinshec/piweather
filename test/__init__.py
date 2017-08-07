import piweather
import unittest
from sqlalchemy import create_engine


class TransientDBTestCase(unittest.TestCase):

    def setUp(self):
        piweather.db = create_engine('sqlite:///:memory:')
        if not piweather.scheduler.running:
            piweather.scheduler.start()

    def tearDown(self):
        for job in piweather.scheduler.get_jobs():
            job.remove()
