""" Helper functions for module """

import requests
import json
import time


def get_tokens(client_id, client_secret, tokens_filepath, code):
    """ Gets the Strava tokens from a json file and
    refreshes them if expired """

    try:
        # Get the tokens from file to connect to Strava
        with open(tokens_filepath) as json_file:
            strava_tokens = json.load(json_file)

    except FileNotFoundError:
        strava_tokens = get_first_time_tokens(client_id, client_secret, code,
                                              tokens_filepath)

    # If access_token has expired then use the refresh_token to get
    # the new access_token
    if strava_tokens['expires_at'] < time.time():

        # Make Strava auth API call with current refresh token
        response = requests.post(
            url='https://www.strava.com/oauth/token',
            data={
                'client_id': int(client_id),
                'client_secret': client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': strava_tokens['refresh_token']
            }
        )

        # Save response as json in new variable
        new_strava_tokens = response.json()

        # Save new tokens to file
        with open(tokens_filepath, 'w') as outfile:
            json.dump(new_strava_tokens, outfile)

        # Use new Strava tokens from now
        strava_tokens = new_strava_tokens

    return strava_tokens


def get_first_time_tokens(client_id, client_secret, code, tokens_filepath):
    """ Gets the Strava tokens for the first time """

    # Make Strava auth API call with URL code from OAuth Authorization page
    response = requests.post(
        url='https://www.strava.com/oauth/token',
        data={
            'client_id': int(client_id),
            'client_secret': client_secret,
            'grant_type': 'authorization_code',
            'code': code
        }
    )

    # Save response as json in new variable
    strava_tokens = response.json()
    print(strava_tokens)

    # Save tokens to json file
    with open(tokens_filepath, 'w') as outfile:
        json.dump(strava_tokens, outfile)

    return strava_tokens
