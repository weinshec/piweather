import dash_core_components as dcc
import pandas as pd
import plotly.graph_objs as go


def default_layout(xlabel="timestamp", ylabel=None, since=None):
    layout_dict = dict(
        legend=dict(x=0.05, y=1.1, orientation="h"),
        hovermode='closest',
        margin=go.Margin(l=50, r=50, b=100, t=20, pad=4),
        xaxis={'title': xlabel},
        yaxis={'title': ylabel},
    )
    if since is not None:
        layout_dict["xaxis"]["range"] = [since, pd.Timestamp.now()]
    return layout_dict


class Single(dcc.Graph):

    def __init__(self, measurement, since):
        data = measurement.data(since=since)
        super(Single, self).__init__(
            id="graph_{}".format(measurement.table),
            figure={
                "data": [
                    go.Scatter(x=data["time"], y=data["value"])
                ],
                "layout": go.Layout(
                    default_layout(ylabel=measurement.label, since=since)
                )
            },
        )


class Statistical(dcc.Graph):

    def __init__(self, measurement, since=None):
        data = measurement.data(since=since)
        super(Statistical, self).__init__(
            id="graph_{}".format(measurement.table),
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
                "layout": go.Layout(
                    default_layout(ylabel=measurement.label, since=since)
                )
            }
        )
