import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import piweather

from datetime import datetime, timedelta


def create_app():
    app = dash.Dash(piweather.config.TITLE)
    app.title = piweather.config.TITLE
    app.css.append_css({
        "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
    app.layout = serve_layout
    return app


def serve_layout():
    viewport = getattr(piweather.config, "VIEWPORT", timedelta(hours=24))
    ts = datetime.now() - viewport

    panel_map = {
        piweather.measurements.Single: SinglePanel,
        piweather.measurements.Statistical: StatisticalPanel,
    }

    layout = list()
    layout.append(
        html.H1(piweather.config.TITLE, style={'textAlign': 'center'}))
    measurements = getattr(piweather.config, "MEASUREMENTS", [])
    for measurement in measurements:
        layout.append(panel_map[type(measurement)](measurement, since=ts))

    return html.Div(layout, className="container")


class Panel(html.Div):

    graph_layout = {
        "legend": dict(x=0.05, y=1.1, orientation="h"),
        "hovermode": "closest",
        "margin": go.Margin(l=50, r=50, b=100, t=20, pad=4),
        "xaxis": {"title": "timestamp"},
    }

    def __init__(self, measurement, since, *args, **kwargs):
        self.measurement = measurement
        self.since = since
        self.graph_layout.update(yaxis={"title": measurement.label})
        self.graph_layout["xaxis"].update(range=[since, datetime.now()])
        super(Panel, self).__init__(self.create_layout(), *args, **kwargs)

    def create_layout(self):
        return [self.graph()]

    def graph(self):
        raise NotImplementedError("Override this in subclass")


class SinglePanel(Panel):

    def graph(self):
        data = self.measurement.data(self.since)
        if data is None:
            data = {"time": [], "value": []}
        return dcc.Graph(
            id="graph_{}".format(self.measurement.table),
            figure={
                "data": [go.Scatter(x=data["time"], y=data["value"])],
                "layout": go.Layout(self.graph_layout),
            },
        )


class StatisticalPanel(Panel):

    def graph(self):
        data = self.measurement.data(self.since)
        if data is None:
            data = {"time": [], "mean": [], "std": [], "min": [], "max": []}
        return dcc.Graph(
            id="graph_{}".format(self.measurement.table),
            figure={
                "data": [
                    go.Scatter(x=data["time"], y=data["mean"],
                               mode="markers", name="mean",
                               error_y=dict(
                                   type="data",
                                   array=data["std"],
                                   visible=True,
                               )),
                    go.Scatter(x=data["time"], y=data["min"],
                               mode="lines", name="min"),
                    go.Scatter(x=data["time"], y=data["max"],
                               mode="lines", name="max"),
                ],
                "layout": go.Layout(self.graph_layout),
            },
        )
