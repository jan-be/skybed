import logging
import os
import threading

import plotly.graph_objects as go
from dash import Dash, dcc, callback, Output, Input

from skybed.uas_position_updater import scenario

logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Dash()

app.layout = [
    dcc.Graph(id='graph-content', style={'height': '100vh'}),
    dcc.Interval(id='interval', interval=1000, n_intervals=0)
]


@callback(
    Output('graph-content', 'figure'),
    Input('interval', 'n_intervals')
)
def update_graph(value):
    fig = go.Figure(go.Scattermap(
        lat=[gnb_position.latitude for gnb_position in scenario.gnb_positions] + [uav.position.latitude for uav in
                                                                                  scenario.uavs],
        lon=[gnb_position.longitude for gnb_position in scenario.gnb_positions] + [uav.position.longitude for uav in
                                                                                   scenario.uavs],
        mode='markers',
        marker={
            "size": [15] * len(scenario.gnb_positions) + [15] * len(scenario.uavs),  # Arrow size
            "color": ["red"] * len(scenario.gnb_positions) + ["green"] * len(scenario.uavs),
            # "color_discrete_sequence": ["red"] * len(scenario.gnb_positions) + ["blue"] * len(scenario.uavs),
            "symbol": ["circle"] * len(scenario.gnb_positions) + ["airport"] * len(scenario.uavs),
            "angle": [0] * len(scenario.gnb_positions) + [uav.direction for uav in scenario.uavs],
            "allowoverlap": True
        },
        text=["Tower 1", "Tower 2", "Tower 3"] + [f"UAV ID: {uav.uav_id}" for uav in scenario.uavs],
    ))

    fig.update_layout(
        autosize=True,
        hovermode='closest',
        map=dict(
            style="https://tiles.stadiamaps.com/styles/outdoors.json?api_key=YOUR-API-KEY",
            bearing=0,
            center=dict(
                lat=52.20572798737899,
                lon=13.15873017619153
            ),
            pitch=0,
            # zoom=5
            zoom=14
        ),
    )
    return fig


def run_map_server_thread():
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 8050}, daemon=True).start()


if __name__ == '__main__':
    run_map_server_thread()
