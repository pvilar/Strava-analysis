""" Functions to create custom maps """

import pydeck as pdk
import pandas as pd
import numpy as np


def create_map(df_coordinates: pd.DataFrame):
    """
    :param df_coordinates: dataframe containing longitudes and latitudes
    :return: Deck object
    """

    lats = df_coordinates['latitude']
    lons = df_coordinates['longitude']
    centroide = _get_centroid(lats, lons)
    zoom = _get_zoom_level(lats, lons)

    df_coordinates['points'] = [
        [x, y] for x, y in zip(  # <-- Points have to be Lon/Lat !!!!!
            df_coordinates.longitude, df_coordinates.latitude)
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

    view_state = pdk.ViewState(latitude=centroide['lat'],
                               longitude=centroide['lon'],
                               zoom=zoom)

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
        layers=layers,
        initial_view_state=view_state,
        tooltip={"text": "{name}"})

    return (r)


def _get_centroid(lats: np.array, lons: np.array):
    maxlon, minlon = max(lons), min(lons)
    maxlat, minlat = max(lats), min(lats)
    center = {
        'lon': round((maxlon + minlon) / 2, 6),
        'lat': round((maxlat + minlat) / 2, 6)
    }
    return center


def _get_zoom_level(lats: np.array, lons: np.array):
    """
    source: https://stackoverflow.com/questions/6048975/google-maps-v3-how-to-calculate-the-zoom-level-for-a-given-bounds
    https://community.plotly.com/t/scattermapbox-setting-visible-range/6140/2
    :param lats: array of points latitues
    :param lons: array of points longitudes
    :return: zoom level to fit bounds in the map
    """

    bounds = [max(lats), max(lons), min(lats), min(lons)]

    ne_lat = bounds[0]
    ne_long = bounds[1]
    sw_lat = bounds[2]
    sw_long = bounds[3]

    scale = 1.5
    WORLD_DIM = {'height': 256 * scale, 'width': 256 * scale}
    ZOOM_MAX = 20

    def latRad(lat):
        sin = np.sin(lat * np.pi / 180)
        radX2 = np.log((1 + sin) / (1 - sin)) / 2
        return max(min(radX2, np.pi), -np.pi) / 2

    def zoom(mapPx, worldPx, fraction):
        return np.floor(np.log(mapPx / worldPx / fraction) / np.log(2))

    latFraction = (latRad(ne_lat) - latRad(sw_lat)) / np.pi

    lngDiff = ne_long - sw_long
    lngFraction = ((lngDiff + 360) if lngDiff < 0 else lngDiff) / 360

    mapDim = {'height': 500, 'width': 500}

    latZoom = zoom(mapDim['height'], WORLD_DIM['height'], latFraction)
    lngZoom = zoom(mapDim['width'], WORLD_DIM['width'], lngFraction)

    return min(latZoom, lngZoom, ZOOM_MAX)
