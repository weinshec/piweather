from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine

scheduler = BackgroundScheduler()
scheduler.start()

db = create_engine('sqlite:///:memory:')
