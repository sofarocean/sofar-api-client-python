"""
File for utility functions and classes
"""
import json
import requests
from pywavefleet import get_endpoint, get_token


class Query:
    """
    General Query class
    """
    def __init__(self, spotter_id : str, variables: list = None, limit: int = 20, include_all: bool = False):
        self._params = {}
        self.spotter_id = spotter_id
        self.waves = include_all
        self.winds = include_all
        self.track = include_all
        self.frequency = include_all
        self.directional_moments = include_all
        self.limit = limit

        if variables is not None and not include_all:
            for var in variables:
                self._add_var(var)

    def _add_var(self, var_name: str):
        var_name = var_name.lower()
        if var_name in ('wave', 'waves'):
            self.waves(True)
        elif var_name in ('wind', 'winds'):
            self.winds(True)
        elif var_name in ('frequency', 'frequencies'):
            self.frequency(True)
        elif var_name in ('directionalmoment', 'directionalmoments', 'directional_moment', 'directional_moments'):
            self.directional_moments(True)
        elif var_name == 'track':
            self.track(True)
        else:
            raise Exception('Invalid Query Variable')

    @property
    def waves(self):
        return self.waves

    @waves.setter
    def waves(self, include: bool):
        self.waves = include

    @property
    def winds(self):
        return self.winds

    @winds.setter
    def winds(self, include: bool):
        self.winds = include

    @property
    def track(self):
        return self.track

    @track.setter
    def track(self, include: bool):
        self.track = include

    @property
    def directional_moments(self):
        return self.directional_moments

    @directional_moments.setter
    def directional_moments(self, include: bool):
        self.directional_moments = include

    @property
    def frequency(self):
        return self.frequency

    @frequency.setter
    def frequency(self, include: bool):
        self.frequency = include

    @property
    def limit(self):
        return self.limit

    @limit.setter
    def limit(self, new_limit: int):
        self.limit = new_limit


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
