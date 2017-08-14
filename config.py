from piweather.measurements import Single, Statistical
from piweather.sensors import Dummy

sensors = {
    "dummy0": Dummy(),
    "dummy1": Dummy(),
}

measurements = {
    "dummy0_single": Single(
        sensors["dummy0"],
        frequency=5,
        table="dummy0_single",
    ),
    "dummy1_statistical": Statistical(
        sensors["dummy1"],
        frequency=1,
        n=10,
        table="dummy1_statistical"
    ),
}
