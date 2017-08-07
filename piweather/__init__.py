from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine

scheduler = BackgroundScheduler()
db = create_engine('sqlite:///:memory:')
