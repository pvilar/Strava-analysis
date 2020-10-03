""" Functions for segments analysis """

import sys

import pandas as pd
import requests
import re


def sort_segments_from_activity(activity_id, gender, strava_tokens):

    # get segments from activity
    df_segments = _get_segments_from_activity(activity_id, strava_tokens)

    # filtering 10 random segments to avoid eceeding the rate limit (remove
    # in production)
    df_segments = df_segments.sample(n=10)

    # calculate delta from leader
    print("Sorting segments...")
    df_segments["segment_time_delta"] = df_segments.apply(
        lambda x: _calculate_time_difference_from_leader(x["segment.id"],
                                                         x["elapsed_time"],
                                                         gender=gender,
                                                         strava_tokens=strava_tokens
                                                         ),
        axis=1)

    # sort dataframe
    df_segments.sort_values(by=['segment_time_delta'], inplace=True)
    print("Sorting segments...done!")

    return df_segments


def _check_rate_limit_exceeded(req):

    if "message" in req:
        print(req['message'])

        if req['message'] == "Rate Limit Exceeded":
            sys.exit("Reached the Strava requests limit, stopping execution")


def _get_segments_from_activity(activity_id, strava_tokens):

    print("Loading segments")

    # store URL for activities endpoint
    base_url = "https://www.strava.com/api/v3/"
    endpoint = "activities/{}".format(activity_id)
    url = base_url + endpoint

    # access token
    access_token = strava_tokens['access_token']

    # define headers and parameters for request
    headers = {"Authorization": "Bearer {}".format(access_token)}

    # make GET request to Strava API
    req = requests.get(url, headers=headers).json()

    # check if rate limit is exceeded
    _check_rate_limit_exceeded(req)

    print("Segments loaded successfully")

    return pd.json_normalize(req['segment_efforts'])


def _get_sec(time_str):
    """ Get Seconds from time """

    if time_str.find("s") == -1:
        try:
            h, m, s = time_str.split(':')
            return int(h) * 3600 + int(m) * 60 + int(s)
        except ValueError:
            m, s = time_str.split(':')
            return int(m) * 60 + int(s)
    else:
        return [int(s) for s in re.findall(r'-?\d+\.?\d*', time_str)][0]


def _calculate_time_difference_from_leader(segment_id, athlete_elapsed_time,
                                           gender, strava_tokens):
    """
    Gets the time of the segment's leader in seconds and calculates
    the percent difference from the anthlete time
    """

    # store URL for activities endpoint
    base_url = "https://www.strava.com/api/v3/"
    endpoint = "segments/{}".format(segment_id)
    url = base_url + endpoint

    # access token
    access_token = strava_tokens['access_token']

    # define headers and parameters for request
    headers = {"Authorization": "Bearer {}".format(access_token)}

    # make GET request to Strava API
    req = requests.get(url, headers=headers).json()

    # check if rate limit is exceeded
    _check_rate_limit_exceeded(req)

    # get leader time
    leader_elapsed_time = _get_sec(
        req['xoms']['qom']) if gender == 'women' else _get_sec(req['xoms']['kom'])

    return athlete_elapsed_time / leader_elapsed_time - 1
