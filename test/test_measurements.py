import pandas as pd
import time
import unittest
from sqlalchemy import create_engine
from unittest.mock import patch, PropertyMock

import piweather
from piweather import measurements
from piweather import sensors


class TestMeasurements(unittest.TestCase):

    def setUp(self):
        piweather.db = create_engine('sqlite:///:memory:')

    def tearDown(self):
        for job in piweather.scheduler.get_jobs():
            job.remove()

    def assertNumberOfJobs(self, n):
        self.assertEquals(len(piweather.scheduler.get_jobs()), n)

    def test_measurement_specifying_frequency_adds_job_to_scheduler(self):
        self.assertNumberOfJobs(0)
        single = measurements.Single(sensors.Dummy(), frequency=60)
        self.assertNumberOfJobs(1)
        self.assertEquals(single.frequency, 60)

    def test_measurement_changing_frequency_does_not_add_another_job(self):
        single = measurements.Single(sensors.Dummy(), frequency=60)
        self.assertNumberOfJobs(1)
        single.frequency = 120
        self.assertNumberOfJobs(1)

    def test_measurement_with_0_frequency_does_not_have_a_job(self):
        single = measurements.Single(sensors.Dummy(), frequency=60)
        self.assertNumberOfJobs(1)
        single.frequency = 0
        self.assertNumberOfJobs(0)

    @patch("piweather.sensors.Dummy.value", new_callable=PropertyMock)
    def test_measurement_job_calls_sensors_value(self, mock_value):
        measurements.Single(sensors.Dummy(), frequency=0.1)
        time.sleep(0.2)
        mock_value.assert_called()

    def test_measurement_creates_db_table_on_first_query(self):
        s = measurements.Single(sensors.Dummy(), table="dummy_table")
        s.acquire()
        self.assertTrue(piweather.db.has_table("dummy_table"))

    def test_measurement_fills_database_row(self):
        s = measurements.Single(sensors.Dummy(), table="dummy_table")
        s.acquire()
        s.acquire()
        with piweather.db.connect() as conn, conn.begin():
            data = pd.read_sql_table("dummy_table", conn)
        self.assertEqual(len(data), 2)

    # def test_statistical_measurement_polls_sensor_multiple_times(self):
        # stat = measurements.Statistical(sensors.Dummy(), poll=0.1)
