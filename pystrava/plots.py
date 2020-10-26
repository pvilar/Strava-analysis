""" Functions for plotting """

import logging

import pandas as pd
import numpy as np
import plotly.express as px

logger = logging.getLogger("pystrava")


def plot_segments_insights(data, y, ylabel, title=None):

    if y == "elapsed_time":
        data['elapsed_time'] = pd.to_datetime(data['elapsed_time'])

    elif y == "segment.distance":
        data["segment.distance"] = np.round(data["segment.distance"] / 1000, 2)

    fig = px.scatter(data,
                     x="difference_from_leader",
                     y=y,
                     color='terrain',
                     labels={
                         "difference_from_leader":
                         "Percent Difference from Leader",
                         y: ylabel,
                         "terrain": "Terrain type"
                     },
                     title=title,
                     hover_data=["name"])
    fig.update_xaxes(range=[0, min(2, max(data["difference_from_leader"]))],
                     tickformat='%')

    if y == "elapsed_time":
        fig.update_yaxes(tickformat="%H:%M:%S")

    fig.update_layout(shapes=[
        dict(type='line',
             yref='paper',
             y0=0,
             y1=1,
             xref='x',
             x0=0,
             x1=0,
             line=dict(
                 color="Red",
                 width=3,
                 dash="dash",
             ))
    ])

    fig.add_annotation(text="KOM/QOM",
                       xref="x",
                       yref="paper",
                       x=0.0,
                       y=1.08,
                       showarrow=False,
                       font={
                           "size": 16,
                           "color": "red"
                       })

    return fig
