"""
Sofar Devices
"""
from pywavefleet import SofarConnection
from pywavefleet.tools import parse_date
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


class Query(SofarConnection):
    """
    General Query class
    """
    def __init__(self, spotter_id: str, limit: int = 20, start_date=None, end_date=None):
        super().__init__()
        self.spotter_id = spotter_id
        self.limit = limit

        self.start_date = start_date
        self.end_date = end_date

        self._params = {
            'spotterId': spotter_id,
            'limit': limit,
            'includeWaves': 'true',
            'includeWindData': 'false',
            'includeTrack': 'false',
            'includeFrequencyData': 'false',
            'includeDirectionalMoments': 'false'
        }

        if start_date is not None:
            self._params.update({'startDate': start_date})

        if end_date is not None:
            self._params.update({'endDate': end_date})

    def execute(self):
        scode, data = self._get('wave-data', params=self._params)

        if scode != 200:
            raise QueryError(data['message'])

        return data

    def limit(self, value: int):
        """
        Sets the limit on how many query results to return

        Defaults to 20
        Max of 500 if tracking or waves-standard
        Max of 100 if frequency data is included
        """
        self.limit = value
        self._params.update({'limit': value})

    def waves(self, include: bool):
        """

        :param include: True if you want the query to include waves
        """
        self._params.update({'includeWaves': str(include).lower()})

    def wind(self, include: bool):
        """

        :param include: True if you want the query to include wind data
        """
        self._params.update({'includeWindData': str(include).lower()})

    def track(self, include: bool):
        """

        :param include: True if you want the query to include tracking data
        """
        self._params.update({'includeTrack': str(include).lower()})

    def frequency(self, include: bool):
        """

        :param include: True if you want the query to include frequency data
        """
        self._params.update({'includeFrequencyData': str(include).lower()})

    def directional_moments(self, include: bool):
        """

        :param include: True if you want the query to include directional moment data
        """
        if include and not self._params['includeFrequencyData']:
            print("""Warning: You have currently selected the query to include directional moment data however
                     frequency data is not currently included. \n
                     Directional moment data only applies if the spotter is in full waves/waves spectrum mode. \n 
                     Since the query does not include frequency data (of which directional moments are a subset)
                     the data you have requested will not be included. \n
                     Please set includeFrequencyData to true with .frequency(True) if desired. \n""")
        self._params.update({'includeDirectionalMoments': str(include).lower()})

    def set_start_date(self, new_date: str):
        self._params.update({'startDate': parse_date(new_date)})

    def clear_start_date(self):
        del self._params['startDate']

    def set_end_date(self, new_date: str):
        self._params.update({'endDate': parse_date(new_date)})

    def clear_end_date(self):
        del self._params['endDate']
