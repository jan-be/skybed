import threading

import numpy as np
import plotly.graph_objects as go
from dash import Dash, html, dcc, callback, Output, Input

from ma import world_positions

mapbox_access_token = open(".mapbox_token").read()

app = Dash()

app.layout = [
    html.H1(children='Drooooones', style={'textAlign': 'center'}),
    dcc.Graph(id='graph-content'),
    dcc.Interval(id='interval', interval=1000, n_intervals=0)
]


@callback(
    Output('graph-content', 'figure'),
    Input('interval', 'n_intervals')
)
def update_graph(value):
    fig = go.Figure(go.Scattermapbox(
        lat=np.concat((world_positions.gnb_positions[:, 0], world_positions.uas_positions[:, 0])),
        lon=np.concat((world_positions.gnb_positions[:, 1], world_positions.uas_positions[:, 1])),
        mode='markers',
        marker={"size": [9] * len(world_positions.gnb_positions[:, 0]) + [14] * len(world_positions.uas_positions[:, 0])},
        text=["Tower 1", "Tower 2", "Tower 3"],
    ))

    fig.update_layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=52.20572798737899,
                lon=13.15873017619153
            ),
            pitch=0,
            zoom=14
        ),
    )
    return fig


def run_map_server_async():
    threading.Thread(target=app.run_server, kwargs={'host': '0.0.0.0', 'port': 8050}).start()


if __name__ == '__main__':
    run_map_server_async()
