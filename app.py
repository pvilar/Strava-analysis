import os
import re
import logging
import copy

# import plotly.express as px
import streamlit as st

from pystrava.utils import get_first_time_token, refresh_access_token_if_expired  # noqa: E501
from pystrava.segments import sort_segments_from_activity, format_segments_table  # noqa: E501
from pystrava.transformations import get_segment_coordinates, get_activity_coordinates  # noqa: E501
from pystrava.maps import create_map
from pystrava.plots import plot_segments_insights


def main():
    # Display title and any other information at the top
    st.title("SegmentBreaker")
    st.markdown("## Be The Next Strava Leader")

    # Link to app's OAuth Authorization page
    st.markdown(
        "Click on the following link in order to authorise SegmentBreaker to connect to your Strava"  # noqa: E501
    )
    st.markdown(
        """<a style='display: block; text-align: center;' href="https://www.strava.com/oauth/authorize?client_id=%2053827&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:read_all,activity:read_all" target="_blank">AUTHORIZATION LINK</a>""",  # noqa: E501
        unsafe_allow_html=True,  # when set to True, the url is opened in the same tab  # noqa: E501
    )

    # Text box to input URL from auth
    oauth_response = st.text_input(
        "Enter the URL you got after authorizing the app to access your training data"  # noqa: E501
    )
    if not oauth_response:
        st.warning('Please input the URL you got after authorizing the app')
    else:
        CODE = re.search('code=(.*)&', oauth_response).group(1)

        # TODO: select activity from date?
        # get activity id from user input
        ACTIVITY_ID = st.text_input(
            "Enter an activity id from your trainings"
        )  # ,'4074378152')  # remove default activity id in production

        if not ACTIVITY_ID:
            st.warning('Please input a valid activity id from your profile')
            # st.stop()
        else:
            # TODO: Check if activity id is valid (trying to pull data
            # from the activity id)
            try:
                # Refresh tokens if expired or don't have tokens yet
                tokens = call_refresh_access_token_if_expired(tokens)
                logger.info("Refreshing tokens if necessary")
            except NameError:
                # get tokens
                tokens = call_get_first_time_token(
                    CODE)  # only need to call this once!

            # display map from activity
            df_activity_coordinates = get_activity_coordinates(
                ACTIVITY_ID, tokens)
            st.header("Activity map")
            # st.map(df_activity_coordinates)
            activity_map = create_map(df_activity_coordinates, 'dark')
            st.pydeck_chart(activity_map)

            # TODO: add segments type filter (gender, climbs, remove short
            # segments, remove long segments, downhill)

            # returns the sorted segments by time delta
            filter_type = 'climbs'
            GENDER = 'mens'
            pr_filter = None
            df_segments = copy.deepcopy(
                call_segments_sorting(tokens=tokens,
                                      activity_id=ACTIVITY_ID,
                                      gender=GENDER,
                                      filter_type=filter_type,
                                      pr_filter=pr_filter))

            # TODO: format segments dataframe to show only valuable information
            # displays the segments dataframe with a checkbox to select on the
            # distance of the segment
            st.header("Ranked segments by proximity to Strava leader")
            # distance = st.selectbox(
            #     "Get segments above certain distance in KM:",
            #     range(0, int(max(df_segments['distance']))))
            # df_segments_filtered = df_segments[df_segments['distance'] >= distance]  # noqa: E501
            # df_segments_filtered = df_segments
            st.write(format_segments_table(df_segments))

            # select segment to analyse
            segment_name = st.selectbox("Select a segment to visualize",
                                        df_segments["name"].unique())

            # get segment id from name
            segment_id = df_segments.loc[df_segments['name'] == segment_name,
                                         'segment.id'].values[0]

            # display segment map
            df_segment_coordinates = get_segment_coordinates(
                str(segment_id), tokens)
            st.header("Segment map")
            # st.map(df_segment_coordinates)
            segment_map = create_map(df_segment_coordinates, 'outdoors')
            st.pydeck_chart(segment_map)

            # Segment insights plots
            st.header(
                "How the distance of the segment impacts your proximity to the Strava leader"  # noqa: E501
            )
            st.plotly_chart(
                plot_segments_insights(df_segments, "segment.distance",
                                       "Segment Distance (Km)"))

            st.header(
                "How the distance of the segment impacts your proximity to the Strava leader"  # noqa: E501
            )
            st.plotly_chart(
                plot_segments_insights(df_segments, "elapsed_time",
                                       "Time (hh:mm:ss)"))

            st.header(
                "How the average grade of the segment impacts your proximity to the Strava leader"  # noqa: E501
            )
            st.plotly_chart(
                plot_segments_insights(df_segments, "segment.average_grade",
                                       "Average grade (%)"))

            st.header(
                "How the elevation difference of the segment impacts your proximity to the Strava leader"  # noqa: E501
            )
            st.plotly_chart(
                plot_segments_insights(df_segments, "elevation_difference",
                                       "Elevation Difference (m)"))
            st.header(
                "How the average power varies with the proximity to the Strava leader"  # noqa: E501
            )
            st.plotly_chart(
                plot_segments_insights(df_segments, "average_watts",
                                       "Average Power (W)"))


@st.cache
def call_get_first_time_token(CODE):
    return get_first_time_token(CODE)


@st.cache
def call_refresh_access_token_if_expired(tokens):
    return refresh_access_token_if_expired(tokens)


# This functions calls the function that sorts the segments from the pystrava
# module. In order to apply the cache option, the function that loads the data
# needs to be defined in this script (so it's a workaround to use
# sort_segments_from_activity() cached
@st.cache
def call_segments_sorting(tokens, activity_id, gender, filter_type, pr_filter):
    return sort_segments_from_activity(tokens=tokens,
                                       activity_id=activity_id,
                                       gender=gender,
                                       filter_type=filter_type,
                                       pr_filter=pr_filter)


# General parameters
# ACTIVITY_ID = '4074378152'
GENDER = 'man'  # TODO: add to app as a checkbox or similar
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

logger = logging.getLogger("pystrava")

if __name__ == "__main__":
    main()
