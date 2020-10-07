""" Helper functions for module """

import os
import requests
import time
import sys

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


def get_first_time_token(CODE):
    """ Gets the Strava tokens for the first time """

    # Make Strava auth API call with URL code from OAuth Authorization page
    response = requests.post(url='https://www.strava.com/oauth/token',
                             data={
                                 'client_id': int(CLIENT_ID),
                                 'client_secret': CLIENT_SECRET,
                                 'grant_type': 'authorization_code',
                                 'code': CODE
                             }).json()

    return {
        k: response[k]
        for k in set(['access_token', 'expires_at', 'refresh_token'])
        & set(response.keys())
    }


def refresh_access_token_if_expired(tokens):
    """ Refreshes strava tokens if time expired """

    # If access_token has expired then use the refresh_token to get
    # the new access_token
    if int(tokens['expires_at']) < time.time():

        # Make Strava auth API call with current refresh token
        response = requests.post(url='https://www.strava.com/oauth/token',
                                 data={
                                     'client_id': int(CLIENT_ID),
                                     'client_secret': CLIENT_SECRET,
                                     'grant_type': 'refresh_token',
                                     'refresh_token': tokens['refresh_token']
                                 })

        new_tokens = {
            k: response[k]
            for k in set(['access_token', 'expires_at', 'refresh_token'])
            & set(response.keys())
        }

        return new_tokens
    else:
        return tokens


def check_rate_limit_exceeded(req):

    if "message" in req:
        print(req['message'])

        if req['message'] == "Rate Limit Exceeded":
            sys.exit("Reached the Strava requests limit, stopping execution")
