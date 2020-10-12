""" Functions for segments analysis """

import requests
import re
import logging
from datetime import timedelta

import pandas as pd
import numpy as np

from pystrava.utils import check_rate_limit_exceeded

logger = logging.getLogger("pystrava")


def sort_segments_from_activity(tokens,
                                activity_id,
                                gender='men',
                                pr_filter=1):

    # get segments from activity
    df_segments = _get_segments_from_activity(activity_id, tokens)

    # filtering 10 random segments to avoid eceeding the rate limit (remove
    # in production)
    # df_segments = df_segments.sample(n=20)  # TODO: remove limit

    # filter by PR (3, 2, 1)
    if pr_filter in [1, 2, 3]:
        df_segments = df_segments[df_segments['pr_rank'] <= pr_filter]

    # calculate delta from leader
    logger.info("Sorting segments...")
    df_segments["leader_time"] = df_segments.apply(
        lambda x: _get_time_from_leader(
            x["segment.id"], x["elapsed_time"], gender=gender, tokens=tokens),
        axis=1)

    # time delta
    df_segments["difference_from_leader"] = df_segments[
        "elapsed_time"] / df_segments["leader_time"] - 1

    # select relevant columns
    df_segments = df_segments[[
        'name', 'segment.city', 'pr_rank', 'distance', 'elapsed_time',
        'leader_time', 'difference_from_leader'
    ]]

    # ditance to km
    df_segments['distance'] = df_segments['distance'] / 1000

    # calculate speeds
    df_segments['speed'] = df_segments['distance'] / (
        df_segments['elapsed_time'] / 3600)
    df_segments['leader_speed'] = df_segments['distance'] / (
        df_segments['leader_time'] / 3600)

    # time format
    df_segments['elapsed_time'] = df_segments['elapsed_time'].apply(
        lambda x: str(timedelta(seconds=x)))
    df_segments['leader_time'] = df_segments['leader_time'].apply(
        lambda x: str(timedelta(seconds=x)))

    # sort dataframe
    df_segments.sort_values(by=['difference_from_leader'], inplace=True)

    # format columns
    df_segments = df_segments.style.format({
        'distance': "{:.2f}",
        'pr_rank': "{:.0f}",
        'difference_from_leader': "{:.1%}",
        'speed': "{:.2f}",
        'leader_speed': "{:.2f}"
    })

    logger.info("Sorting segments...done!")

    return df_segments


def _get_segments_from_activity(activity_id, tokens):

    logger.info("Loading segments...")

    # store URL for activities endpoint
    base_url = "https://www.strava.com/api/v3/"
    endpoint = "activities/{}".format(activity_id)
    url = base_url + endpoint

    # define headers and parameters for request
    headers = {"Authorization": "Bearer {}".format(tokens["access_token"])}

    # make GET request to Strava API
    req = requests.get(url, headers=headers).json()

    # check if rate limit is exceeded
    check_rate_limit_exceeded(req)

    logger.info("Loading segments...done!")

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


def _get_time_from_leader(segment_id, athlete_elapsed_time,
                          gender, tokens):
    """
    Gets the time of the segment's leader in seconds and calculates
    the percent difference from the anthlete time
    """

    # store URL for activities endpoint
    base_url = "https://www.strava.com/api/v3/"
    endpoint = "segments/{}".format(segment_id)
    url = base_url + endpoint

    # define headers and parameters for request
    headers = {"Authorization": "Bearer {}".format(tokens["access_token"])}

    # make GET request to Strava API
    req = requests.get(url, headers=headers).json()

    # check if rate limit is exceeded
    check_rate_limit_exceeded(req)

    # get leader time
    leader_elapsed_time = _get_sec(
        req['xoms']['qom']) if gender == 'women' else _get_sec(
            req['xoms']['kom'])

    return leader_elapsed_time
