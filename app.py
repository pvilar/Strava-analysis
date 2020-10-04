import os
import requests
import webbrowser
import re

# import plotly.express as px
import streamlit as st
import polyline
import pandas as pd

from pystrava.utils import get_tokens
from pystrava.segments import _check_rate_limit_exceeded, sort_segments_from_activity


def main():
    # Display title and any other information at the top
    st.title("Be The Next Strava Leader")
    st.markdown("Further description")

    # Link to app's OAuth Authorization page
    url_oauth = 'https://www.strava.com/oauth/authorize?client_id=%2053827&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:read_all,activity:read_all'
    if st.button('Authorize SegmentBreaker to connect to your Strava'):
        webbrowser.open_new_tab(url_oauth)

    # Text box to input URL from auth
    url_code = st.text_input("Enter the URL you got after authorizing the app to access your training data")
    if not url_code:
        st.stop()
    code = re.search('code=(.*)&', url_code).group(1)
    print(code)

    # get tokens
    strava_tokens = get_tokens(CLIENT_ID, CLIENT_SECRET, TOKENS_FILEPATH, code)

    # TODO: select activity from date?
    # get activity id from user input
    ACTIVITY_ID = st.text_input("Enter an activity id from your trainings")#,
                                # '4074378152')  # remove default activity id in production
    if not ACTIVITY_ID:
        st.warning('Please input a valid activity id from your profile')
        st.stop()

    # display map from activity
    df_activity_coordinates = get_activity_coordinates(ACTIVITY_ID, strava_tokens)
    st.header("Activity map")
    st.map(df_activity_coordinates)

    # returns the sorted segments by time delta
    # @st.cache
    # df_segments = sort_segments_from_activity(ACTIVITY_ID, GENDER,
    # strava_tokens)
    df_segments = call_segments_sorting(ACTIVITY_ID, strava_tokens)

    # TODO: format segments dataframe to show only valuable information
    # displays the segments dataframe with a checkbox to select on the
    # distance of the segment
    st.header("Ranked segments by proximity to Strava leader")
    distance = st.selectbox("Get segments above certain distance in KM:",
                            range(0, int(max(df_segments['distance']/1000))))
    df_segments_filtered = df_segments[df_segments['distance']/1000 >= distance]
    st.write(df_segments_filtered)

    # select segment to analyse
    segment_name = st.selectbox("Select a segment to visualize",
                                df_segments_filtered["name"].unique())

    # get segment id from name
    segment_id = df_segments_filtered.loc[
                        df_segments_filtered['name'] == segment_name,
                        'segment.id'].values[0]

    # display segment map
    df_segment_coordinates = get_segment_coordinates(str(segment_id), strava_tokens)
    st.header("Segment map")
    st.map(df_segment_coordinates)


def get_activity_coordinates(activity_id, strava_tokens):

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

    # activity polyline
    activity_polyline = req['map']["polyline"]

    # coordinates = polyline.decode(activity_polyline)
    coordinates = polyline.decode(activity_polyline)

    return pd.DataFrame(coordinates, columns=["latitude", "longitude"])


def get_segment_coordinates(segment_id, strava_tokens):

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

    # segment polyline
    segment_polyline = req['map']["polyline"]

    # coordinates = polyline.decode(activity_polyline)
    coordinates = polyline.decode(segment_polyline)

    return pd.DataFrame(coordinates, columns=["latitude", "longitude"])


# This functions calls the function that sorts the segments from the pystrava
# module. In order to apply the cache option, the function that loads the data
# needs to be defined in this script (so it's a workaround to use
# sort_segments_from_activity() cached
@st.cache
def call_segments_sorting(ACTIVITY_ID, strava_tokens):
    return sort_segments_from_activity(activity_id=ACTIVITY_ID, gender=GENDER,
                                       strava_tokens=strava_tokens)

# General parameters
# ACTIVITY_ID = '4074378152'
GENDER = 'man'
TOKENS_FILEPATH = os.getenv("TOKENS_FILEPATH")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

if __name__ == "__main__":
    main()
