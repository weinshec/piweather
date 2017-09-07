import logging
import piweather
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy import Integer, Float, DateTime


DTYPE_MAP = {
    int: Integer,
    float: Float,
    datetime: DateTime,
}


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


def map_dtype(dtype):
    if dtype not in DTYPE_MAP:
        raise TypeError("No column known to map for '{}'".format(dtype))
    return DTYPE_MAP[dtype]
