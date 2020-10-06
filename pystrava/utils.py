""" Helper functions for module """

import os
import requests
import time
import sys

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


def get_first_time_token():
    """ Gets the Strava tokens for the first time """

    if not os.getenv("ACCESS_TOKEN"):

        print("code inside get_first_time_token function: " + os.getenv("CODE"))  # remove

        # Make Strava auth API call with URL code from OAuth Authorization page
        response = requests.post(
            url='https://www.strava.com/oauth/token',
            data={
                'client_id': int(CLIENT_ID),
                'client_secret': CLIENT_SECRET,
                'grant_type': 'authorization_code',
                'code': os.getenv("CODE")
            }
        ).json()

        print("response inside get_first_time_token func:")
        print(response)

        # TODO: check if code exprired and require anotherone (can only be used once?)

        # Save response as env vars
        os.environ["ACCESS_TOKEN"] = response['access_token']
        os.environ['EXPIRES_AT'] = str(response['expires_at'])
        os.environ['REFRESH_TOKEN'] = response['refresh_token']

        print("access token in function: "+os.getenv("ACCESS_TOKEN"))
        print("EXPIRES_AT in function: "+os.getenv('EXPIRES_AT'))

    return


def refresh_access_token_if_expired():
    """ Refreshes strava tokens if time expired """

    # If access_token has expired then use the refresh_token to get
    # the new access_token
    if int(os.getenv("EXPIRES_AT")) < time.time():

        # Make Strava auth API call with current refresh token
        response = requests.post(
            url='https://www.strava.com/oauth/token',
            data={
                'client_id': int(CLIENT_ID),
                'client_secret': CLIENT_SECRET,
                'grant_type': 'refresh_token',
                'refresh_token': os.getenv("REFRESH_TOKEN")
            }
        )

        # Save response as env vars
        os.environ["ACCESS_TOKEN"] = response['access_token']
        os.environ['EXPIRES_AT'] = str(response['expires_at'])
        os.environ['REFRESH_TOKEN'] = response['refresh_token']

    return


def check_rate_limit_exceeded(req):

    if "message" in req:
        print(req['message'])

        if req['message'] == "Rate Limit Exceeded":
            sys.exit("Reached the Strava requests limit, stopping execution")
