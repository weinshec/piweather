import unittest
import piweather
import piweather.dashboard


class TestDashApp(unittest.TestCase):

    def setUp(self):
        piweather.main.load_config("test/static/config.py")
        piweather.app = piweather.dashboard.create_app()
        piweather.app.server.testing = True
        self.client = piweather.app.server.test_client()

    def test_app_return_response_code_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_app_has_correct_title(self):
        response = self.client.get("/")
        self.assertIn(piweather.config.TITLE.encode("utf-8"), response.data)