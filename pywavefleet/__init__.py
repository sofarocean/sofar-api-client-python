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
    def __init__(self):
        self.token = get_token()
        self.endpoint = get_endpoint()
        self.header = {'token': self.token, 'Content-Type': 'application/json'}

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
