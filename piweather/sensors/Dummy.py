import random
from piweather.sensors import Sensor


class Dummy(Sensor):

    dtypes = {
        "random": float,
        "randint": int,
    }

    def __init__(self, *args, **kwargs):
        super(Dummy, self).__init__(*args, **kwargs)

    def read(self):
        return {
            "random": random.random(),
            "randint": random.randint(0, 5)
        }
