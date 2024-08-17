import logging
import threading

import plotly.graph_objects as go
from dash import Dash, dcc, callback, Output, Input

from ma.uas_position_updater import uavs_data, gnb_positions

logging.getLogger('werkzeug').setLevel(logging.ERROR)

mapbox_access_token = open(".mapbox_token").read()

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
    fig = go.Figure(go.Scattermapbox(
        lat=[gnb_position.latitude for gnb_position in gnb_positions] + [uav.position.latitude for uav in uavs_data],
        lon=[gnb_position.longitude for gnb_position in gnb_positions] + [uav.position.longitude for uav in uavs_data],
        mode='markers',
        marker={"size": [8] * len(gnb_positions) + [14] * len(uavs_data)},
        text=["Tower 1", "Tower 2", "Tower 3"] + [f"UAV ID: {uav.uav_id}" for uav in uavs_data],
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
