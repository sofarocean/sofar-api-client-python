"""
Sofar Devices
"""
import json
import requests
from pywavefleet import get_endpoint, get_token
from pywavefleet.api import SofarConnection, Query
from pywavefleet.wavefleet_exceptions import QueryError, CouldNotRetrieveFile


class SofarApi(SofarConnection):
    def __init__(self):
        super().__init__()
        self._spotters = self._devices()

    # ---------------------------------- GET --------------------------------------- #
    def grab_datafile(self, spotter_id: str, start_date: str, end_date: str):
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

    def get_latest_data(self, spotter_id: str, include_directional_moments: bool = False):
        params = {'spotterId': spotter_id}

        if include_directional_moments:
            params['includeDirectionalMoments'] = 'true'

        scode, results = self._get('/latest-data', params=params)

        if scode != 200:
            raise QueryError(results['message'])

        data = results['data']

        return data


    def get_spotter_data(self, query: Query, start_date: str, end_date: str):
        # TODO
        pass

    def get_device_ids(self):
        """

        :return: List of ids associated with the environment token
        """
        return [device['spotterId'] for device in self._spotters]

    def get_devices(self):
        """

        :return:
        """
        spotters = [Spotter(device['spotterId'], device['name'], data={}) for device in self._spotters]
        # TODO: init based on ids
        return spotters

    # ---------------------------------- POST -------------------------------------- #
    def update_spotter_name(self, spotter_id, new_spotter_name):
        body = {
            "spotterId": spotter_id,
            "name": new_spotter_name
        }

        scode, response = self._post("change-name", body)
        message = response['message']

        if scode != 200:
            raise QueryError(f"{message}")

        print(f"{spotter_id} updated with name: {response['data']['name']}")

        return new_spotter_name

    def _devices(self):
        scode, data = self._get('/devices')

        if scode != 200:
            raise QueryError(data['message'])

        _spotters = data['data']['devices']

        return _spotters


class Spotter:
    def __init__(self, spotter_id: str, name: str):
        self.id = spotter_id
        self.name = name

        self.mode = None
        self.data = None
        self.lat = None
        self.lon = None
        self.battery_power = None
        self.solar_voltage = None
        self.humidity = None
        self._session = SofarApi()
        self._params = {

        }

    # -------------------------- Properties -------------------------------------- #
    @property
    def mode(self):
        """
        The tracking type of the spotter.
        3 Modes are possible:
            - waves-standard
            - waves-full (Includes spectrum data)
            - tracking

        :return: The current mode of the spotter
        """
        return self.mode

    @mode.setter
    def mode(self, value): self.mode = value

    @property
    def lat(self):
        """

        :return: The most recent latitude value (since updating)
        """
        return self.lat

    @lat.setter
    def lat(self, latitude): self.lat = latitude

    @property
    def lon(self):
        """

        :return: The most recent longitude value (since updating)
        """
        return self.lon

    @lon.setter
    def lon(self, longitude): self.lon = longitude

    @property
    def battery_power(self):
        """

        :return: The most recent battery_power value (since updating)
        """
        return self.battery_power

    @battery_power.setter
    def battery_power(self, value): self.battery_power = value

    @property
    def solar_voltage(self):
        """

        :return: The most recent solar voltage level (since updating)
        """
        return self.solar_voltage

    @solar_voltage.setter
    def solar_voltage(self, value): self.solar_voltage = value

    @property
    def humidity(self):
        """

        :return: The most recent humidity value (since updating)
        """
        return self.humidity

    @humidity.setter
    def humidity(self, value): self.humidity = value

    # -------------------------- API METHODS -------------------------------------- #
    def change_name(self, new_name):
        """
        Updates the spotters name in the Sofar Database

        :param new_name: The new desired spotter name
        """
        self.name = self._session.update_spotter_name(self.id, new_name)

    def download_datafile(self, start_date, end_date):
        """
        Download a datafile container this spotters data from start_date to end_date

        :param start_date: Start date string
        :param end_date: End date String
        """
        self._session.grab_datafile(self.id, start_date, end_date)

    def update(self):
        """
        Updates the spotter's data values

        :return: The updated spotter object
        """
        data = self._session.get_latest_data(self.id)

        self.name = data['spotterName']
        self.mode = data['payloadType']
        self.humidity = data['']
        self.solar_voltage = data['']
        self.battery_power = data['']
        self.humidity = data['']

        pass

    def add_wave_data(self, startDate):
        pass