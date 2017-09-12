import dash_html_components as html
import piweather

from piweather.dashboard import Title, MeasurementTable, ScatterPlot
from piweather.helper import get_viewport_since


def layout():
    layout = [
        Title(),
        MeasurementTable(piweather.config.MEASUREMENTS[0]),
        ScatterPlot(
            [
                ("dummy0_table/random", {"name": "foobar"}),
                ("dummy1_table/randint", {"mode": "lines"})
            ],
            ylabel="some random numbers",
            since=get_viewport_since())
    ]

    return html.Div(layout, className="container")
