import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import piweather
import uuid

from piweather import Measurement
from piweather.helper import get_viewport_since


def create_app():
    app = dash.Dash(piweather.config.TITLE)
    app.title = piweather.config.TITLE
    app.css.append_css({
        "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
    return app


class Title(html.H1):

    style = {"textAlign": "center"}

    def __init__(self, *args, **kwargs):
        super(Title, self).__init__(piweather.config.TITLE, *args, **kwargs)


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


class ScatterPlot(dcc.Graph):

    graph_layout = {
        "legend": dict(x=0.05, y=1.1, orientation="h"),
        "hovermode": "closest",
        "margin": go.Margin(l=50, r=50, b=100, t=20, pad=4),
        "xaxis": {"title": "timestamp"},
    }

    def __init__(self, sources=[], since=None, ylabel="", *args, **kwargs):
        plots = []
        for (source, kw) in sources:
            table, column = source.split("/")
            data = Measurement.retrieve_data(
                table, column=["time", column], since=since)
            kw.setdefault("mode", "markers")
            kw.setdefault("name", source)
            plots.append(go.Scatter(x=data["time"], y=data[column], **kw))

        self.graph_layout["yaxis"] = dict(title=ylabel)
        kwargs.setdefault("id", str(uuid.uuid4()))

        super(ScatterPlot, self).__init__(
            figure={"data": plots, "layout": go.Layout(self.graph_layout)},
            *args, **kwargs
        )


def default_layout():
    layout = [Title()]

    for measurement in getattr(piweather.config, "MEASUREMENTS", []):
        columns = measurement.sensor.dtypes.keys()
        layout.append(
            ScatterPlot(
                sources=[
                    ("{}/{}".format(measurement.table, c), {})
                    for c in columns],
                since=get_viewport_since(),
            )
        )

    return html.Div(layout, className="container")
