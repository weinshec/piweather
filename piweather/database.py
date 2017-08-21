import logging
import piweather
from sqlalchemy import create_engine


def get_engine(url=None):
    if piweather.db is None:

        if url is not None:
            db_url = url
        elif piweather.config is not None:
            db_url = piweather.config.DB_ENGINE
        else:
            logging.error("No DB_ENGINE url specified")
            raise RuntimeError
        piweather.db = create_engine(db_url)

    return piweather.db
