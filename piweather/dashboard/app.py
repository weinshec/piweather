import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import piweather as pw
import plotly.graph_objs as go


def serve_layout():
    # TODO: Make timedelta a global setting
    ts = pd.Timestamp.now() - pd.Timedelta(days=1)
    data = pw.measurement_list["dummy0_single"].data(since=ts)

    return html.Div([
        html.H1("piweather|AWS"),
        dcc.Graph(
            id="dummy0_single",
            figure={
                "data": [
                    go.Scatter(
                        x=data["time"],
                        y=data["value"],
                        mode='markers',
                        opacity=0.7,
                        marker={
                            'size': 15,
                            'line': {'width': 0.5, 'color': 'white'}
                        },
                    )
                ],
                "layout": go.Layout(
                    xaxis={'title': 'timestamp'},
                    yaxis={'title': 'value'},
                    margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                    legend={'x': 0, 'y': 1},
                    hovermode='closest'
                )
            }
        )
    ])


app = dash.Dash()
app.layout = serve_layout
