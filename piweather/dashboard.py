import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import piweather
import uuid

from piweather.helper import get_viewport


def create_app():
    app = dash.Dash(piweather.config.TITLE)
    app.title = piweather.config.TITLE
    app.css.append_css({
        "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
    return app


def default_layout():
    layout = [TitleBar()]

    for measurement in getattr(piweather.config, "MEASUREMENTS", []):
        layout.append(
            Graph([Scatter(measurement, c) for c in measurement.columns])
        )

    return html.Div(layout, className="container")


class TitleBar(html.H1):

    style = {"textAlign": "center"}

    def __init__(self, *args, **kwargs):
        super(TitleBar, self).__init__(piweather.config.TITLE, *args, **kwargs)


class MeasurementTable(html.Table):

    style = {
        "margin-left": "auto",
        "margin-right": "auto",
    }

    def __init__(self, measurement, *args, **kwargs):

        cell_style = dict(textAlign="center")

        header = []
        values = []

        for name, value in measurement.last.items():
            header.append(html.Th(name, style=cell_style))

            if name == "time":
                format_str = "{:%d-%m-%Y %H:%M:%S}"
            elif measurement.sensor.dtypes[name] == float:
                format_str = "{:0.2f}"
            else:
                format_str = "{}"
            values.append(html.Td(format_str.format(value), style=cell_style))

        table = [html.Tr(header), html.Tr(values)]

        super(MeasurementTable, self).__init__(table, *args, **kwargs)


class Graph(dcc.Graph):

    graph_layout = {
        "legend": dict(x=0.05, y=1.1, orientation="h"),
        "hovermode": "closest",
        "margin": go.Margin(l=50, r=50, b=100, t=20, pad=4),
        "xaxis": {"title": "timestamp"},
    }

    def __init__(self, plots=[], ylabel="", *args, **kwargs):
        self.graph_layout["yaxis"] = dict(title=ylabel)
        kwargs.setdefault("id", str(uuid.uuid4()))

        super(Graph, self).__init__(
            figure={"data": plots, "layout": go.Layout(self.graph_layout)},
            *args, **kwargs
        )


class Scatter(go.Scatter):

    def __init__(self, measurement, column, **kwargs):
        data = measurement.data(columns=["time", column],
                                since=get_viewport())
        kwargs.setdefault("mode", "markers")
        kwargs.setdefault("name", column)
        super(Scatter, self).__init__(x=data["time"], y=data[column], **kwargs)
