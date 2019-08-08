"""
File for utility functions and classes
"""
import json
import requests
from . import get_endpoint, get_token
from pywavefleet.wavefleet_exceptions import QueryError, CouldNotRetrieveFile


class Query:
    def __init__(self, variables: list = None, limit: int = 100, include_all: bool = False):
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


class SofarApi:
    def __init__(self):
        self.token = get_token()
        self.endpoint = get_endpoint()
        self.header = {'token': self.token, 'Content-Type': 'application/json'}
        self._spotters = self._devices()

    # GET
    def get_device_ids(self):
        """

        :return: List of ids associated with the environment token
        """
        return [device['spotterId'] for device in self._spotters]

    def get_devices(self):
        """

        :return:
        """
        from pywavefleet.sofar import Spotter
        spotters = [Spotter(device['spotterId'], device['name'], data={}) for device in self._spotters]
        # TODO: init based on ids
        return spotters

    def get_datafile(self, spotter_id : str, start_date: str, end_date: str):
        """

        :param spotter_id:
        :return: None if not completed, else the url
        """
        import urllib.request
        import shutil

        body = {
            "spotterId": spotter_id,
            "startDate": start_date,
            "endDate": end_date
        }

        scode, response = self._post("history", body)

        if scode != 200:
            raise QueryError(f"{response['message']}")

        file_id = response['data']['fileId']

        scode, response = self._get(f"datafile/{file_id}")

        status = response['fileStatus']
        file_url = response['fileUrl']

        if status != "complete":
            raise CouldNotRetrieveFile(f"File creation not yet complete. Try {file_url} in a little bit")

        file_name = f"{spotter_id}_{start_date}_{end_date}"
        with urllib.request.urlopen(file_url) as response, open(file_name, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        return f"{file_name} downloaded successfully"

    def get_latest_data(self, spotter_id: str):
        pass

    def get_spotter_data(self, query: Query, start_date: str, end_date: str):
        pass

    # POST
    def change_name(self, spotter_id, new_spotter_name):
        body = {
            "spotterId": spotter_id,
            "name": new_spotter_name
        }

        scode, response = self._post("change-name", body)
        message = response['message']

        if scode != 200:
            raise QueryError(f"{message}")

        name = response['data']['name']
        assert(new_spotter_name == name)

    # Helper methods
    def _get(self, endpoint_suffix):
        response = requests.get(f"{self.endpoint}/{endpoint_suffix}", headers=self.header)
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

    def _devices(self):
        from pywavefleet.wavefleet_exceptions import QueryError

        scode, data = self._get('/devices')

        if scode != 200:
            raise QueryError(data['message'])

        _spotters = data['data']['devices']

        return _spotters













def time_stamp_to_epoch( date_string ):
    """

    :param date_string: Date string formatted as iso
    :return:
    """
    import time
    import calendar

    return calendar.timegm(time.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ'))



