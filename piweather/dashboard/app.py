import dash
import dash_html_components as html
import pandas as pd
import piweather as pw
import piweather.dashboard.panels as panels


def create_panel(measurement, since):
    if isinstance(measurement, pw.measurements.Single):
        return html.Div(panels.Single(measurement, since))
    elif isinstance(measurement, pw.measurements.Statistical):
        return html.Div(panels.Statistical(measurement, since))


def serve_layout():

    # TODO: Make timestamp selectable in config
    ts = pd.Timestamp.now() - pd.Timedelta(days=1)

    panels = list()
    for measurement in pw.config.MEASUREMENTS:
        panels.append(create_panel(measurement, since=ts))

    return html.Div([
        html.H1("piweather|AWS",
                style={'textAlign': 'center'}),
        *panels
    ], className="container")

app = dash.Dash()
app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})
app.layout = serve_layout
