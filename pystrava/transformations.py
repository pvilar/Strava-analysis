""" Functions for working with coordinates """

import os
import requests

import pandas as pd
import polyline

from pystrava.utils import refresh_access_token_if_expired
from pystrava.segments import check_rate_limit_exceeded


def get_activity_coordinates(activity_id):

    # store URL for activities endpoint
    base_url = "https://www.strava.com/api/v3/"
    endpoint = "activities/{}".format(activity_id)
    url = base_url + endpoint

    # define headers and parameters for request
    refresh_access_token_if_expired()
    headers = {"Authorization": "Bearer {}".format(os.getenv("ACCESS_TOKEN"))}

    # make GET request to Strava API
    req = requests.get(url, headers=headers).json()

    # check if rate limit is exceeded
    check_rate_limit_exceeded(req)

    # activity polyline
    activity_polyline = req['map']["polyline"]

    # coordinates = polyline.decode(activity_polyline)
    coordinates = polyline.decode(activity_polyline)

    return pd.DataFrame(coordinates, columns=["latitude", "longitude"])


def get_segment_coordinates(segment_id):

    # store URL for activities endpoint
    base_url = "https://www.strava.com/api/v3/"
    endpoint = "segments/{}".format(segment_id)
    url = base_url + endpoint

    # define headers and parameters for request
    refresh_access_token_if_expired()
    headers = {"Authorization": "Bearer {}".format(os.getenv("ACCESS_TOKEN"))}

    # make GET request to Strava API
    req = requests.get(url, headers=headers).json()

    # check if rate limit is exceeded
    check_rate_limit_exceeded(req)

    # segment polyline
    segment_polyline = req['map']["polyline"]

    # coordinates = polyline.decode(activity_polyline)
    coordinates = polyline.decode(segment_polyline)

    return pd.DataFrame(coordinates, columns=["latitude", "longitude"])