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

    layout = list()
    layout.append(
        html.H1(piweather.config.TITLE, style={'textAlign': 'center'}))
    measurements = getattr(piweather.config, "MEASUREMENTS", [])
    for measurement in measurements:
        layout.append(Panel(measurement, since=ts))

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
        self.graph_layout["xaxis"].update(range=[since, datetime.now()])
        super(Panel, self).__init__(self.create_layout(), *args, **kwargs)

    def create_layout(self):
        return [self.graph()]

    def graph(self):
        data = self.measurement.data(self.since)

        plots = []
        for name, values in data.items():
            if name == "time":
                continue
            plots.append(
                go.Scatter(x=data["time"], y=values, mode="lines", name=name)
            )

        return dcc.Graph(
            id="graph_{}".format(self.measurement.table),
            figure={
                "data": plots,
                "layout": go.Layout(self.graph_layout),
            },
        )
