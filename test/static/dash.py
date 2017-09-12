import dash_html_components as html
import piweather

from piweather.dashboard import TitleBar, MeasurementTable, Graph, Scatter


def layout():
    measurements = piweather.config.MEASUREMENTS

    layout = [
        TitleBar(),
        MeasurementTable(measurements[0]),
        Graph(
            [
                Scatter(measurements[0], "random", mode="lines"),
                Scatter(measurements[1], "randint", name="integer"),
            ],
            ylabel="some random numbers",)
    ]

    return html.Div(layout, className="container")
