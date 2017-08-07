from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine

scheduler = BackgroundScheduler()
# db = create_engine('sqlite:///:memory:')
db = create_engine('sqlite:////tmp/piweather.sqlite3')

sensor_list = dict()
measurement_list = dict()
