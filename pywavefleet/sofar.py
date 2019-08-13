"""
Sofar Devices
"""
from pywavefleet import get_endpoint, get_token
from pywavefleet.query import Query
from pywavefleet.api import SofarConnection
from pywavefleet.wavefleet import Spotter
from pywavefleet.wavefleet_exceptions import QueryError, CouldNotRetrieveFile


class SofarApi(SofarConnection):
    def __init__(self):
        super().__init__()
        self._spotters = self._devices()
        self.devices = None

    def grab_datafile(self, spotter_id: str, start_date: str, end_date: str):
        """

        :param spotter_id: The id of the spotter
        :param start_date: The start date of the data to be included
        :param end_date: The end date of the data to be included
        :return: None if not completed, else the url
        """
        # TODO: If the generation of the file isn't instantaneous, will fail
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

    def get_latest_data(self, spotter_id: str,
                        include_wind_data: bool = False,
                        include_directional_moments: bool = False):
        params = {'spotterId': spotter_id}

        if include_directional_moments:
            params['includeDirectionalMoments'] = 'true'

        if include_wind_data:
            params['includeWindData'] = 'true'

        scode, results = self._get('/latest-data', params=params)

        if scode != 200:
            raise QueryError(results['message'])

        data = results['data']

        return data

    def get_wave_data(self):
        # TODO: For all spotters?
        pass

    def get_wind_data(self):
        # TODO: For all spotters?
        pass

    def get_frequency_data(self):
        # TODO: for all spotters?
        pass

    def get_all_spotter_data(self):
        # TODO: Get data for all spotters
        pass

    def get_device_ids(self):
        """

        :return: List of ids associated with the environment token
        """
        return [device['spotterId'] for device in self._spotters]

    def get_devices(self, update: bool = False):
        """

        :param update: If cached data exists, then either return that (update = False) or query to gain the most
                       recent data (update = True or (update = False and self.devices = None) )
                       and update the cache

        :return: A list of the spotter objects associated with this account
        """
        if self.devices is not None and not update:
            return self.devices

        spotter_names = {device['spotter']: device['name'] for device in self._spotters}
        status_code, data = self._get('device-radius')

        if status_code != 200:
            raise QueryError(data['message'])

        spot_data = data['devices']

        spotter_objs = []
        for device in spot_data:
            _id = device['spotterId']
            _name = spotter_names[_id]

            sptr = Spotter(_id, _name)
            sptr.lat(device['location']['lat'])
            sptr.lon(device['location']['lon'])
            sptr.update_timestamp(device['location']['timestamp'])

            spotter_objs.append(sptr)

        self.devices = spotter_objs

        # TODO: still need to get mode somehow
        return spotter_objs

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

    # ---------------------------------- Helper Functions -------------------------------------- #
    def _devices(self):
        scode, data = self._get('/devices')

        if scode != 200:
            raise QueryError(data['message'])

        _spotters = data['data']['devices']

        return _spotters


