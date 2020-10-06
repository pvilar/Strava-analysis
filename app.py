import os
import webbrowser
import re

# import plotly.express as px
import streamlit as st

from pystrava.utils import get_first_time_token
from pystrava.segments import sort_segments_from_activity
from pystrava.transformations import get_segment_coordinates, get_activity_coordinates


def main():
    # Display title and any other information at the top
    st.title("SegmentBreaker")
    st.markdown("## Be The Next Strava Leader")

    # Link to app's OAuth Authorization page
    url_oauth = 'https://www.strava.com/oauth/authorize?client_id=%2053827&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:read_all,activity:read_all'
    # if st.button('Authorize SegmentBreaker to connect to your Strava'):
        # webbrowser.open_new_tab(url_oauth)
    st.markdown("Click on the following link in order to authorise SegmentBreaker to connect to your Strava")
    st.markdown(url_oauth)

    # Text box to input URL from auth
    oauth_response = st.text_input("Enter the URL you got after authorizing the app to access your training data")
    if not oauth_response:
        st.stop()
    url_code = re.search('code=(.*)&', oauth_response).group(1)
    print("first time code: "+url_code)

    # Set code as environment variable
    os.environ["CODE"] = url_code

    # get tokens
    print("access token in app (should be empty): "+os.getenv("ACCESS_TOKEN"))
    get_first_time_token()
    print("access token in app: "+os.getenv("ACCESS_TOKEN"))

    # TODO: select activity from date?
    # get activity id from user input
    ACTIVITY_ID = st.text_input("Enter an activity id from your trainings") #,'4074378152')  # remove default activity id in production

    if not ACTIVITY_ID:
        st.warning('Please input a valid activity id from your profile')
        # st.stop()
    else:
        # display map from activity
        df_activity_coordinates = get_activity_coordinates(ACTIVITY_ID)
        st.header("Activity map")
        st.map(df_activity_coordinates)

        # returns the sorted segments by time delta
        df_segments = call_segments_sorting(ACTIVITY_ID)

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
        df_segment_coordinates = get_segment_coordinates(str(segment_id))
        st.header("Segment map")
        st.map(df_segment_coordinates)

# This functions calls the function that sorts the segments from the pystrava
# module. In order to apply the cache option, the function that loads the data
# needs to be defined in this script (so it's a workaround to use
# sort_segments_from_activity() cached
@st.cache
def call_segments_sorting(ACTIVITY_ID):
    return sort_segments_from_activity(activity_id=ACTIVITY_ID, gender=GENDER)

# General parameters
# ACTIVITY_ID = '4074378152'
GENDER = 'man'
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

if __name__ == "__main__":
    main()
