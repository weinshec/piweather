from piweather import Measurement
from piweather.sensors import Dummy

SENSORS = {
    "dummy0": Dummy(),
    "dummy1": Dummy(),
}

MEASUREMENTS = [
    Measurement(
        SENSORS["dummy0"],
        frequency=5,
        table="dummy0_table",
    ),
    Measurement(
        SENSORS["dummy1"],
        frequency=1,
        table="dummy1_table",
    ),
]
