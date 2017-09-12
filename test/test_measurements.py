import datetime
import time
from unittest.mock import patch, PropertyMock

import piweather
from piweather import Measurement
from piweather import sensors
from test import TransientDBTestCase


class TestMeasurements(TransientDBTestCase):

    def assertNumberOfJobs(self, n):
        self.assertEqual(len(piweather.scheduler.get_jobs()), n)

    def test_measurement_specifying_frequency_adds_job_to_scheduler(self):
        self.assertNumberOfJobs(0)
        meas = Measurement(
            sensors.Dummy(), table="dummy", frequency=60)
        self.assertNumberOfJobs(1)
        self.assertEqual(meas.frequency, 60)

    def test_measurement_changing_frequency_does_not_add_another_job(self):
        meas = Measurement(
            sensors.Dummy(), table="dummy", frequency=60)
        self.assertNumberOfJobs(1)
        meas.frequency = 120
        self.assertNumberOfJobs(1)

    def test_measurement_with_0_frequency_does_not_have_a_job(self):
        meas = Measurement(
            sensors.Dummy(), table="dummy", frequency=60)
        self.assertNumberOfJobs(1)
        meas.frequency = 0
        self.assertNumberOfJobs(0)

    @patch("piweather.sensors.Dummy.value", new_callable=PropertyMock)
    def test_measurement_job_calls_sensors_value(self, mock_value):
        Measurement(sensors.Dummy(), table="dummy", frequency=0.1)
        time.sleep(0.2)
        self.assertTrue(mock_value.called)

    def test_measurement_creates_db_table_on_initialization(self):
        Measurement(sensors.Dummy(), table="dummy_table")
        self.assertTrue(piweather.db.has_table("dummy_table"))

    def test_measurement_not_raises_if_table_exists(self):
        Measurement(sensors.Dummy(), table="dummy_table")
        Measurement(sensors.Dummy(), table="dummy_table")

    def test_measurment_has_last_acquisition_stored(self):
        m = Measurement(sensors.Dummy(), table="dummy_table")
        self.assertEqual(m.last, {})
        m.acquire()
        self.assertIn("time", m.last)
        for key in sensors.Dummy.dtypes.keys():
            self.assertIn(key, m.last)

    def test_measurement_fills_database_rows(self):
        m = Measurement(sensors.Dummy(), table="dummy_table")
        m.acquire()
        m.acquire()
        self.assertEqual(len(m.data()["random"]), 2)

    def test_can_query_measurements_from_db(self):
        m = Measurement(sensors.Dummy(), table="query_table")
        m.acquire()
        time.sleep(0.1)
        ts = datetime.datetime.now()
        time.sleep(0.1)
        m.acquire()

        self.assertEqual(len(m.data()["random"]), 2)
        self.assertEqual(len(m.data(since=ts)["random"]), 1)

    def test_data_returns_dict_even_if_table_is_empty(self):
        m = Measurement(sensors.Dummy(), table="empty_table")
        data = m.data()
        self.assertIn("time", data)
        self.assertListEqual(data["time"], [])

    def test_can_retrieve_subset_of_columns(self):
        m = Measurement(sensors.Dummy(), table="dummy_table")
        m.acquire()

        with self.subTest("list argument"):
            data = m.data(columns=["randint"])
            self.assertNotIn("random", data)

        with self.subTest("string argument"):
            data = m.data(columns="randint")
            self.assertNotIn("random", data)
