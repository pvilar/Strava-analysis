""" Functions to create custom maps """

import pydeck as pdk
import pandas as pd


def create_map(df_coordinates):

    def get_centroid(lat, lon):
        return (sum(lat) / len(lat), sum(lon) / len(lon))

    lat = df_coordinates['latitude']
    lon = df_coordinates['longitude']
    centroide = get_centroid(lat, lon)

    df_coordinates['points'] = [
        [x, y] for x, y in zip(  # <-- Points have to be Lon/Lat !!!!!
            df_coordinates.longitude,
            df_coordinates.latitude)
    ]

    flat_list = []
    for p in df_coordinates['points']:
        flat_list.append(p)

    df_path = pd.DataFrame({
        'name': 'Strava Activity',
        'color': '#ed1c24',
        'path': [flat_list]
    })

    def hex_to_rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    df_path["color"] = df_path["color"].apply(hex_to_rgb)

    view_state = pdk.ViewState(latitude=centroide[0],
                               longitude=centroide[1],
                               zoom=13)

    layers = [
        pdk.Layer(
            type="PathLayer",
            data=df_path,
            pickable=True,
            get_color="color",
            width_scale=40,
            width_min_pixels=1,
            get_path="path",
            get_width=0.3,
        )
    ]

    r = pdk.Deck(
        # "mapbox://styles/mapbox/light-v9",
        map_style='mapbox://styles/mapbox/streets-v11',
        layers=layers,
        initial_view_state=view_state,
        tooltip={"text": "{name}"})

    return(r)
