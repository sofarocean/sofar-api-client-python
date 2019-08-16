"""
This file is part of pysofar: A client for interfacing with Sofar Oceans Spotter API

Contents: Classes used to connect to the Sofar API and return data

Copyright (C) 2019
Sofar Ocean Technologies

Authors: Mike Sosa
"""
from datetime import datetime
from itertools import chain
from multiprocessing.pool import ThreadPool
from pysofar import SofarConnection
from pysofar.tools import parse_date
from pysofar.wavefleet_exceptions import QueryError, CouldNotRetrieveFile


class SofarApi(SofarConnection):
    """
    Class for interfacing with the Sofar Wavefleet API
    """
    def __init__(self):
        super().__init__()
        self.devices = self._devices()

    # ---------------------------------- Simple Device Endpoints -------------------------------------- #
    def get_devices(self):
        """

        :return: Basic data about the spotters belonging to this account
        """
        return self._devices()

    def get_device_ids(self):
        """

        :return: List of ids associated with the clients environment token
        """
        return [device['spotterId'] for device in self.devices]

    def get_device_location_data(self):
        """

        :return: The most recent locations of all spotters belonging to this account
        """
        return self._device_radius()

    # ---------------------------------- Single Spotter Endpoints -------------------------------------- #
    def grab_datafile(self, spotter_id: str, start_date: str, end_date: str):
        """

        :param spotter_id: The string id of the spotter
        :param start_date: ISO8601 formatted start date of the data
        :param end_date: ISO8601 formatted end date of the data

        :return: None if not completed, else the status of the file download
        """
        # TODO: If the generation of the file isn't instantaneous, will fail
        import urllib.request
        import shutil

        # QUERY to request the file
        body = {
            "spotterId": spotter_id,
            "startDate": start_date,
            "endDate": end_date
        }

        scode, response = self._post("history", body)

        if scode != 200:
            raise QueryError(f"{response['message']}")

        file_id = response['data']['fileId']

        # QUERY to download the requested file
        scode, response = self._get(f"datafile/{file_id}")

        status = response['fileStatus']
        file_url = response['fileUrl']

        if status != "complete":
            raise CouldNotRetrieveFile(f"File creation not yet complete. Try {file_url} in a little bit")

        # downloading the file
        file_name = f"{spotter_id}_{start_date}_{end_date}"
        with urllib.request.urlopen(file_url) as response, open(file_name, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        return f"{file_name} downloaded successfully"

    def get_latest_data(self, spotter_id: str,
                        include_wind_data: bool = False,
                        include_directional_moments: bool = False):
        """

        :param spotter_id: The string id of the spotter
        :param include_wind_data: Defaults to False. Set to True if you want the latest data to include wind data
        :param include_directional_moments: Defaults to False. Only applies if the spotter is in 'full_waves' mode.
                                            Set to True if you want the latest data to include directional moments

        :return: The latest data values based on the given parameters from the requested spotter
        """
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

    def update_spotter_name(self, spotter_id, new_spotter_name):
        """
        Update the name of a spotter

        :param spotter_id: The string id of the spotter whose name you want to change
        :param new_spotter_name: The new name to give to the requested spotter

        :return: The new name if the query succeeds else throws an error
        """
        body = {
            "spotterId": spotter_id,
            "name": new_spotter_name
        }

        # request name update
        scode, response = self._post("change-name", body)
        message = response['message']

        if scode != 200:
            raise QueryError(f"{message}")

        print(f"{spotter_id} updated with name: {response['data']['name']}")

        return new_spotter_name

    # ---------------------------------- Multi Spotter Endpoints -------------------------------------- #
    def get_wave_data(self, start_date: str = None, end_date: str = None):
        """
        Get all wave data for related spotters

        :param start_date: ISO8601 start date of data period
        :param end_date: ISO8601 end date of data period

        :return: Wave data as a list
        """
        _ids = self.get_device_ids()
        # defaults to given start date or start of 2000
        st = start_date or '2000-01-01T00:00:00.000Z'
        # defaults to given end date of now
        end = end_date or datetime.utcnow()

        queries = [Query(_id, limit=500, start_date=st, end_date=end) for _id in _ids]

        pool = ThreadPool(processes=16)
        _data = pool.map(_wave_worker, queries)
        pool.close()

        return _data

    def get_wind_data(self, start_date: str = None, end_date: str = None):
        """
        Get all wind data for related spotters

        :param start_date: ISO8601 start date of data period
        :param end_date: ISO8601 end date of data period

        :return: Wind data as a list
        """
        _ids = self.get_device_ids()
        # defaults to given start date or start of 2000
        st = start_date or '2000-01-01T00:00:00.000Z'
        # defaults to given end date of now
        end = end_date or datetime.utcnow()

        queries = [Query(_id, limit=500, start_date=st, end_date=end) for _id in _ids]

        # Set query to include desired params
        for q in queries:
            q.waves(False)
            q.wind(True)

        pool = ThreadPool(processes=16)
        _data = pool.map(_wind_worker, queries)
        pool.close()

        # right now data is list of lists, convert to single list and sort
        _data = list(chain(*_data))

        if len(_data) > 0:
            _data.sort(key=lambda x: x['timestamp'])

        return _data

    def get_frequency_data(self, start_date: str = None, end_date: str = None):
        """
        Get all Frequency data for related spotters

        :param start_date: ISO8601 start date of data period
        :param end_date: ISO8601 end date of data period

        :return: Frequency data as a list
        """
        _ids = self.get_device_ids()
        # defaults to given start date or start of 2000
        st = start_date or '2000-01-01T00:00:00.000Z'
        # defaults to given end date of now
        end = end_date or datetime.utcnow()

        queries = [Query(_id, limit=500, start_date=st, end_date=end) for _id in _ids]

        # Set query to include desired params
        for q in queries:
            q.waves(False)
            q.frequency(True)

        pool = ThreadPool(processes=16)
        _data = pool.map(_frequency_worker, queries)
        pool.close()

        # right now data is list of lists, convert to single list and sort
        _data = list(chain(*_data))

        if len(_data) > 0:
            _data.sort(key=lambda x: x['timestamp'])

        return _data

    def get_track_data(self, start_date: str = None, end_date: str = None):
        """
        Get all track data for related spotters

        :param start_date: ISO8601 start date of data period
        :param end_date: ISO8601 end date of data period

        :return: track data as a list
        """
        _ids = self.get_device_ids()
        # defaults to given start date or start of 2000
        st = start_date or '2000-01-01T00:00:00.000Z'
        # defaults to given end date of now
        end = end_date or datetime.utcnow()

        queries = [Query(_id, limit=500, start_date=st, end_date=end) for _id in _ids]

        # Set query to include desired params
        for q in queries:
            q.waves(False)
            q.track(True)

        pool = ThreadPool(processes=16)
        _data = pool.map(_track_worker, queries)
        pool.close()

        # right now data is list of lists, convert to single list and sort
        _data = list(chain(*_data))

        if len(_data) > 0:
            _data.sort(key=lambda x: x['timestamp'])

        return _data

    def get_all_data(self, start_date: str = None, end_date: str = None):
        """
        Get all data for related spotters

        :param start_date: ISO8601 start date of data period
        :param end_date: ISO8601 end date of data period

        :return: Data as a list
        """
        _ids = self.get_device_ids()
        # defaults to given start date or start of 2000
        st = start_date or '2000-01-01T00:00:00.000Z'
        # defaults to given end date of now
        end = end_date or datetime.utcnow()

        queries = [Query(_id, limit=500, start_date=st, end_date=end) for _id in _ids]

        pool = ThreadPool(processes=16)
        _data = pool.map(_data_worker, queries)
        pool.close()

        # TODO: See results of this and decide whether to reduce
        # # right now data is list of lists, convert to single list and sort
        # _data = list(chain(*_data))
        #
        # if len(_data) > 0:
        #     _data.sort(key=lambda x: x['timestamp'])
        #
        return _data

    def get_spotters(self): return get_and_update_spotters(_api=self)

    # ---------------------------------- Helper Functions -------------------------------------- #
    def _devices(self):
        scode, data = self._get('/devices')

        if scode != 200:
            raise QueryError(data['message'])

        _spotters = data['data']['devices']

        return _spotters

    def _device_radius(self):
        status_code, data = self._get('device-radius')

        if status_code != 200:
            raise QueryError(data['message'])

        spot_data = data['data']['devices']

        return spot_data


class Query(SofarConnection):
    """
    General Query class
    """
    _MISSING = object()

    def __init__(self, spotter_id: str, limit: int = 20, start_date=_MISSING, end_date=_MISSING):
        super().__init__()
        self.spotter_id = spotter_id
        self._limit = limit

        if start_date is self._MISSING or start_date is None:
            self.start_date = None
        else:
            self.start_date = parse_date(start_date)

        if end_date is self._MISSING or end_date is None:
            self.end_date = None
        else:
            self.end_date = parse_date(end_date)

        self._params = {
            'spotterId': spotter_id,
            'limit': limit,
            'includeWaves': 'true',
            'includeWindData': 'false',
            'includeTrack': 'false',
            'includeFrequencyData': 'false',
            'includeDirectionalMoments': 'false'
        }

        if self.start_date is not None:
            self._params.update({'startDate': self.start_date})

        if self.end_date is not None:
            self._params.update({'endDate': self.end_date})

    def execute(self):
        scode, data = self._get('wave-data', params=self._params)

        if scode != 200:
            raise QueryError(data['message'])

        return data['data']

    def limit(self, value: int):
        """
        Sets the limit on how many query results to return

        Defaults to 20
        Max of 500 if tracking or waves-standard
        Max of 100 if frequency data is included
        """
        self._limit = value
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
        self.start_date = parse_date(new_date)
        self._params.update({'startDate': self.start_date})

    def clear_start_date(self):
        self.start_date = None
        if 'startDate' in self._params:
            del self._params['startDate']

    def set_end_date(self, new_date: str):
        self.end_date = parse_date(new_date)
        self._params.update({'endDate': self.end_date})

    def clear_end_date(self):
        if 'endDate' in self._params:
            del self._params['endDate']

    def __str__(self):
        s = f"Query for {self.spotter_id} \n" +\
            f"  Start: {self.start_date or 'From Beginning'} \n" +\
            f"  End: {self.end_date or 'Til Present'} \n" +\
            "  Params:\n" +\
            f"    id: {self._params['spotterId']}\n" +\
            f"    limit: {self._params['limit']} \n" +\
            f"    waves: {self._params['includeWaves']} \n" +\
            f"    wind: {self._params['includeWindData']} \n" +\
            f"    track: {self._params['includeTrack']} \n" +\
            f"    frequency: {self._params['includeFrequencyData']} \n" +\
            f"    directional_moments: {self._params['includeDirectionalMoments']} \n"

        return s


# ---------------------------------- Util Functions -------------------------------------- #
def get_and_update_spotters(_api=None):
    """

    :return: A list of the spotter objects associated with this account
    """

    api = _api or SofarApi()

    # grab device id's and query for device data
    # initialize spotter objects
    spot_data = api.devices

    pool = ThreadPool(processes=16)
    spotters = pool.map(_spot_worker, spot_data)
    pool.close()

    return spotters


# ---------------------------------- Workers -------------------------------------- #
def _spot_worker(device: dict):
    from pysofar.spotter import Spotter

    _id = device['spotterId']
    _name = device['name']

    sptr = Spotter(_id, _name)
    sptr.update()

    return sptr


