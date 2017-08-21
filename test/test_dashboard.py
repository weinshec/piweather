import piweather
import piweather.dashboard
from piweather.helper import load_external

from test import TransientDBTestCase


class TestDashApp(TransientDBTestCase):

    def setUp(self):
        piweather.config = load_external("test/static/config.py")

        super(TestDashApp, self).setUp()

        piweather.app = piweather.dashboard.create_app()
        piweather.app.server.testing = True
        self.client = piweather.app.server.test_client()

    def test_app_return_response_code_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_app_has_correct_title(self):
        response = self.client.get("/")
        self.assertIn(piweather.config.TITLE.encode("utf-8"), response.data)
