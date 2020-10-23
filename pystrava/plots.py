""" Functions for plotting """

import logging

import plotly.express as px

logger = logging.getLogger("pystrava")


def plot_segments_insights(segments_table, x, xlabel, title=None):

    fig = px.scatter(segments_table,
                     x=x,
                     y="difference_from_leader",
                     color='terrain',
                     labels={
                         x: xlabel,
                         "difference_from_leader":
                         "Percent Difference from Leader",
                         "terrain": "Terrain type"
                     },
                     title=title)
    fig.update_yaxes(range=[0, None], tickformat='%')

    return fig
