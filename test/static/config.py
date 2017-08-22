from datetime import timedelta


TITLE = "piweather|AWS"

HOSTS = "0.0.0.0"
PORT = 8050

DB_ENGINE = "sqlite:////tmp/piweather.db"

SENSORS = "test/static/sensors.py"

VIEWPORT = timedelta(hours=24)
