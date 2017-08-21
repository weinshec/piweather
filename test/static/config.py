from piweather.measurements import Single, Statistical
from piweather.sensors import Dummy

TITLE = "piweather|AWS"

SENSORS = {
    "dummy0": Dummy(),
    "dummy1": Dummy(),
}

MEASUREMENTS = [
    Single(
        SENSORS["dummy0"],
        frequency=5,
        table="dummy0_single",
        label="dummy measurement",
    ),
    Statistical(
        SENSORS["dummy1"],
        frequency=1,
        n=10,
        table="dummy1_statistical",
    ),
]

HOSTS = "0.0.0.0"
PORT = 8050
