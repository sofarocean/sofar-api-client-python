"""
This file is part of pysofar: A client for interfacing with Sofar Oceans Spotter API

Copyright (C) 2019
Sofar Ocean Technologies

Authors: Mike Sosa
"""
import os
import dotenv
import requests
import json

# config values
userpath = os.path.expanduser("~")
enviromentFile = os.path.join(userpath, 'sofar_api.env')
dotenv.load_dotenv(enviromentFile)
token = os.getenv('WF_API_TOKEN')

_wavefleet_token = token
_endpoint = 'https://wavefleet.spoondriftspotter.co/api'


def get_token():
    return _wavefleet_token


def get_endpoint():
    return _endpoint


class SofarConnection:
    """
    Base Parent class for connections to the api
    Use SofarApi in sofar.py in practice
    """
    def __init__(self, custom_token=None):
        self._token = custom_token or get_token()
        self.endpoint = get_endpoint()
        self.header = {'token': self._token, 'Content-Type': 'application/json'}

    # Helper methods
    def _get(self, endpoint_suffix, params: dict = None):
        url = f"{self.endpoint}/{endpoint_suffix}"

        if params is None:
            response = requests.get(url, headers=self.header)
        else:
            response = requests.get(url, headers=self.header, params=params)

        status = response.status_code
        data = json.loads(response.text)

        return status, data

    def _post(self, endpoint_suffix, json_data):
        response = requests.get(f"{self.endpoint}/{endpoint_suffix}",
                                json=json_data,
                                headers=self.header)
        status = response.status_code
        data = json.loads(response.text)

        return status, data

    def set_token(self, new_token):
        self._token = new_token
        self.header.update({'token': new_token})


