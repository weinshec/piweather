from piweather.measurements import Single, Statistical
from piweather.sensors import Dummy

sensors = {
    "dummy0": Dummy(),
    "dummy1": Dummy(),
}

measurements = [
    Single(
        sensors["dummy0"],
        frequency=5,
        table="dummy0_single"
    ),
    Statistical(
        sensors["dummy1"],
        frequency=1,
        nSamples=10,
        table="dummy1_single"
    ),
]
