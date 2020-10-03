import os

# import plotly.express as px
import streamlit as st

from pystrava.utils import get_tokens
from pystrava.segments import sort_segments_from_activity


def main():
    # Display title and any other information at the top
    st.title("Be The Next Strava Leader")
    st.markdown("Further description")

    # get tokens
    strava_tokens = get_tokens(CLIENT_ID, CLIENT_SECRET, TOKENS_FILEPATH)

    # get activity id from user input
    ACTIVITY_ID = st.text_input("Enter an activity id from your trainings")
    if not ACTIVITY_ID:
        st.warning('Please input a valid activity id from your profile')
        st.stop()

    # returns the sorted segments by time delta
    # @st.cache
    # df_segments = sort_segments_from_activity(ACTIVITY_ID, GENDER,
    # strava_tokens)
    df_segments = call_segments_sorting(ACTIVITY_ID, strava_tokens)

    # displays the segments dataframe with a checkbox to select on the
    # distance of the segment
    st.header("Ranked segments by proximity to Strava leader")
    distance = st.selectbox("Get segments above certain distance in KM:",
                            range(0, int(max(df_segments['distance']/1000))))
    df_segments_filtered = df_segments[df_segments['distance']/1000 >= distance]
    st.write(df_segments_filtered)


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
