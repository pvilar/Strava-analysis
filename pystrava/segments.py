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
                                gender,
                                filter_type,
                                pr_filter=None):

    # get segments from activity
    df_segments = _get_segments_from_activity(activity_id, tokens)
    logger.info(f"The activity contains {df_segments.shape[0]} segments.")

    # check the number of climb segments
    n_segments_climb = (df_segments['segment.climb_category'] > 0).sum()

    # filtering only categorized climbs if avtivity is Ride
    if n_segments_climb > 0 and filter_type == 'climbs' and df_segments[
            'segment.activity_type'].value_counts().index[0] == 'Ride':
        df_segments = df_segments[df_segments['segment.climb_category'] > 0]
    else:
        df_segments = df_segments.sample(n=30)

    # filter by PR (3, 2, 1)
    if pr_filter in [1, 2, 3]:
        df_segments = df_segments[df_segments['pr_rank'] <= pr_filter]

    logger.info(f"There are {df_segments.shape[0]} segments selected.")

    # calculate delta from leader
    logger.info("Sorting segments...")
    df_segments["leader_time"] = df_segments.apply(
        lambda x: _get_time_from_leader(
            x["segment.id"], gender=gender, tokens=tokens),
        axis=1)

    # time delta
    df_segments["difference_from_leader"] = df_segments[
        "elapsed_time"] / df_segments["leader_time"] - 1

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

    # calculate elevation difference
    df_segments['elevation_difference'] = np.where(
        df_segments['segment.average_grade'] > 0,
        df_segments['segment.elevation_high'] -
        df_segments['segment.elevation_low'],
        -(df_segments['segment.elevation_high'] -
          df_segments['segment.elevation_low']))

    # calculate type of terrain
    df_segments['terrain'] = df_segments.apply(lambda x: calculate_terrain(
        grade=x['segment.average_grade'], elv_diff=x['elevation_difference']),
                                               axis=1)

    logger.info("Sorting segments...done!")

    return df_segments


def format_segments_table(df_segments):

    # select relevant columns
    df_segments_formatted = df_segments[[
        'name', 'segment.city', 'pr_rank', 'distance', 'elapsed_time',
        'leader_time', 'difference_from_leader', 'speed', 'leader_speed'
    ]].reset_index(drop=True)

    # rename columns
    df_segments_formatted = df_segments_formatted.rename(
        columns={
            'name': "Name",
            'segment.city': "City",
            'distance': "Distance (Km)",
            'pr_rank': "PR rank",
            'elapsed_time': "Elapsed Time",
            'leader_time': "Leader Time",
            'difference_from_leader': "Difference from leader",
            'speed': "Speed (Km/h)",
            'leader_speed': "Leader Speed (Km/h)"
        })

    # format columns
    df_segments_formatted = df_segments_formatted.style.format({
        'Distance (Km)':
        "{:.2f}",
        'PR rank':
        "{}",
        'Difference from leader':
        "{:.1%}",
        'Speed (Km/h)':
        "{:.1f}",
        'Leader Speed (Km/h)':
        "{:.1f}"
    })

    return df_segments_formatted


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


def _get_time_from_leader(segment_id, gender, tokens):
    """
    Gets the time of the segment's leader in seconds and calculates
    the percent difference from the anthlete time
    """
    try:
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

    except Exception:
        logger.info(f"Couldn't retrieve the leader elapsed time for the following segment: {segment_id}")  # noqa: E501

        return 0


def calculate_terrain(grade,
                      elv_diff,
                      grade_threshold=1,
                      elv_diff_threshold=20):

    if grade >= grade_threshold and elv_diff >= elv_diff_threshold:
        terrain = 'uphill'
    elif grade <= -grade_threshold and elv_diff <= elv_diff_threshold:
        terrain = 'downhill'
    elif -grade_threshold <= grade <= grade_threshold and -elv_diff_threshold <= elv_diff <= elv_diff_threshold:
        terrain = 'flat'
    else:
        terrain = 'other'

    return terrain
