from apscheduler.schedulers.background import BackgroundScheduler
from piweather.measurements import Measurement  # noqa

scheduler = BackgroundScheduler()
db = None
config = None
app = None
