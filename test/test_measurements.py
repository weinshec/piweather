import datetime
import time
from unittest.mock import patch, PropertyMock

import piweather
from piweather import measurements
from piweather import sensors
from test import TransientDBTestCase


class TestMeasurements(TransientDBTestCase):

    def assertNumberOfJobs(self, n):
        self.assertEqual(len(piweather.scheduler.get_jobs()), n)

    def test_measurement_specifying_frequency_adds_job_to_scheduler(self):
        self.assertNumberOfJobs(0)
        single = measurements.Single(
            sensors.Dummy(), table="dummy", frequency=60)
        self.assertNumberOfJobs(1)
        self.assertEqual(single.frequency, 60)

    def test_measurement_changing_frequency_does_not_add_another_job(self):
        single = measurements.Single(
            sensors.Dummy(), table="dummy", frequency=60)
        self.assertNumberOfJobs(1)
        single.frequency = 120
        self.assertNumberOfJobs(1)

    def test_measurement_with_0_frequency_does_not_have_a_job(self):
        single = measurements.Single(
            sensors.Dummy(), table="dummy", frequency=60)
        self.assertNumberOfJobs(1)
        single.frequency = 0
        self.assertNumberOfJobs(0)

    @patch("piweather.sensors.Dummy.value", new_callable=PropertyMock)
    def test_measurement_job_calls_sensors_value(self, mock_value):
        measurements.Single(sensors.Dummy(), table="dummy", frequency=0.1)
        time.sleep(0.2)
        self.assertTrue(mock_value.called)

    def test_measurement_creates_db_table_on_initialization(self):
        measurements.Single(sensors.Dummy(), table="dummy_table")
        self.assertTrue(piweather.db.has_table("dummy_table"))

    def test_measurement_not_raises_if_table_exists(self):
        measurements.Single(sensors.Dummy(), table="dummy_table")
        measurements.Single(sensors.Dummy(), table="dummy_table")

    def test_measurment_has_last_acquisition_stored(self):
        s = measurements.Single(sensors.Dummy(), table="dummy_table")
        self.assertIsNone(s.last)
        s.acquire()
        self.assertIn("time", s.last)
        self.assertIn("value", s.last)

    def test_measurement_fills_database_rows(self):
        s = measurements.Single(sensors.Dummy(), table="dummy_table")
        s.acquire()
        s.acquire()
        self.assertEqual(len(s.data()["value"]), 2)

    def test_can_query_measurements_from_db(self):
        s = measurements.Single(sensors.Dummy(), table="query_table")
        s.acquire()
        time.sleep(0.1)
        ts = datetime.datetime.now()
        time.sleep(0.1)
        s.acquire()

        self.assertEqual(len(s.data()["value"]), 2)
        self.assertEqual(len(s.data(since=ts)["value"]), 1)


class TestStatisticalMeasurement(TransientDBTestCase):

    def test_statistical_measurement_polls_sensor_multiple_times(self):
        stat = measurements.Statistical(
            sensors.Dummy(), n=2, table="stat_table")
        stat.acquire()
        stat.acquire()
        stat.acquire()
        data = stat.data()
        self.assertEqual(len(data["time"]), 1)
