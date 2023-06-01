"""
This file is part of pysofar: A client for interfacing with Sofar Ocean's Spotter API

Contents: Classes used to connect to the Sofar API and return data

Copyright 2019-2022
Sofar Ocean Technologies

Authors: Mike Sosa et al.
"""
from datetime import datetime
from itertools import chain
from multiprocessing.pool import ThreadPool
from pysofar import SofarConnection
from pysofar.tools import parse_date
from pysofar.wavefleet_exceptions import QueryError, CouldNotRetrieveFile
from typing import List, Tuple, Dict
import warnings


class SofarApi(SofarConnection):
    """
    Class for interfacing with the Sofar Wavefleet API
    """
    def __init__(self, custom_token=None):
        if custom_token is not None:
            super().__init__(custom_token)
        else:
            super().__init__()

        self.devices = []
        self.device_ids = []
        self._sync()

    # ---------------------------------- Simple Device Endpoints -------------------------------------- #
    def get_device_location_data(self):
        """

        :return: The most recent locations of all Spotters belonging to this account
        """
        return self._device_radius()

    # ---------------------------------- Single Spotter Endpoints -------------------------------------- #
    def grab_datafile(self, spotter_id: str, start_date: str, end_date: str):
        """

        :param spotter_id: The string id of the Spotter
        :param start_date: ISO8601 formatted start date of the data
        :param end_date: ISO8601 formatted end date of the data

        :return: None if not completed, else the status of the file download
        """
        # TODO: If the generation of the file isn't instantaneous, will fail
        #  TODO : Look into async.io for potential solution?
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
                        include_directional_moments: bool = False,
                        include_barometer_data: bool = False,
                        include_partition_data: bool = False,
                        include_surface_temp_data: bool = False
                        ):
        """

        :param spotter_id: The string id of the Spotter
        :param include_wind_data: Defaults to False. Set to True if you want the latest data to include wind data
        :param include_directional_moments: Defaults to False. Only applies if the Spotter is in 'full_waves' mode.
                                            Set to True if you want the latest data to include directional moments
        :param include_barometer_data: Defaults to False. Only applies to barometer-equipped Spotters.
        :param include_partition_data: Defaulse to False. Only applies to Spotters in Waves:Partition mode.
        :param include_surface_temp_data: Defaults to False. Only applies to SST sensor-equipped Spotters.

        :return: The latest data values based on the given parameters from the requested Spotter
        """
        params = {'spotterId': spotter_id}

        if include_directional_moments:
            params['includeDirectionalMoments'] = 'true'

        if include_wind_data:
            params['includeWindData'] = 'true'

        if include_barometer_data:
            params['includeBarometerData'] = 'true'

        if include_partition_data:
            params['includePartitionData'] = 'true'

        if include_surface_temp_data:
            params['includeSurfaceTempData'] = 'true'

        scode, results = self._get('/latest-data', params=params)

        if scode != 200:
            raise QueryError(results['message'])

        data = results['data']

        return data

    def get_sensor_data(self, spotter_id: str, start_date: str, end_date: str):
        """

        :param spotter_id: The string id of the Spotter
        :param start_date: ISO8601 formatted start date of the data
        :param end_date: ISO8601 formatted end date of the data

        :return: Data as a json from the requested Spotter
        """
        
        params = {
            "spotterId": spotter_id,
            "startDate": start_date,
            "endDate": end_date
        }

        scode, results = self._get('/sensor-data', params=params)

        if scode != 200:
            raise QueryError(results['message'])

        data = results['data']

        return data

    def update_spotter_name(self, spotter_id, new_spotter_name):
        """
        Update the name of a Spotter

        :param spotter_id: The string id of the Spotter whose name you want to change
        :param new_spotter_name: The new name to give to the requested Spotter

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
    def get_wave_data(self, start_date: str = None, end_date: str = None, params: dict = None):
        """
        Get all wave data for related Spotters

        :param start_date: ISO8601 start date of data period
        :param end_date: ISO8601 end date of data period
        :param params: dict of additional query parameters to write beyond default values

        :return: Wave data as a list
        """
        return self._get_all_data(['waves'], start_date, end_date, params)

    def get_wind_data(self, start_date: str = None, end_date: str = None, params: dict = None):
        """
        Get all wind data for related Spotters

        :param start_date: ISO8601 start date of data period
        :param end_date: ISO8601 end date of data period
        :param params: dict of additional query parameters to write beyond default values

        :return: Wind data as a list
        """
        return self._get_all_data(['wind'], start_date, end_date, params)

    def get_frequency_data(self, start_date: str = None, end_date: str = None, params: dict = None):
        """
        Get all Frequency data for related Spotters

        :param start_date: ISO8601 start date of data period
        :param end_date: ISO8601 end date of data period
        :param params: dict of additional query parameters to write beyond default values

        :return: Frequency data as a list
        """
        return self._get_all_data(['frequency'], start_date, end_date, params)

    def get_track_data(self, start_date: str = None, end_date: str = None, params: dict = None):
        """
        Get all track data for related Spotters

        :param start_date: ISO8601 start date of data period
        :param end_date: ISO8601 end date of data period
        :param params: dict of additional query parameters to write beyond default values

        :return: track data as a list
        """
        return self._get_all_data(['track'], start_date, end_date, params)

    def get_all_data(self, start_date: str = None, end_date: str = None, params: dict = None):
        """
        Get all data for related Spotters

        :param start_date: ISO8601 start date of data period
        :param end_date: ISO8601 end date of data period
        :param params: dict of additional query parameters to write beyond default values

        :return: Data as a list
        """
        return self._get_all_data(['waves', 'wind', 'frequency', 'track'], start_date, end_date, params)

    def get_spotters(self): return get_and_update_spotters(_api=self)

    def search(self, shape:str, shape_params:List[Tuple], start_date:str, end_date:str,
               radius=None, page_size=100,return_generator=False):

        if shape not in ('circle','envelope'):
            raise TypeError('Shape needs to be one of type Circle or Envelope')

        if page_size > 500:
            warnings.warn('Maximum page size is 500')
            page_size=500

        if shape == 'circle' and radius is None:
            raise ValueError('Radius needs to be set when shape is circle')

        # flatten
        if shape == 'envelope':
            vertices = []
            for point in shape_params:
                vertices += point
        elif shape == 'circle':
            vertices = shape_params

        params = {
            'shape':shape,
            # convert list to a comma seperated string of values. Requests does not
            # like iterators as argument.
            'shapeParams':','.join([str(x) for x in vertices]),
            'startDate':start_date,
            'endDate':end_date,
            'pageSize':page_size,
            'radius':radius
        }
        def get_function(endpoint_suffix,params ):
            scode, data = self._get(endpoint_suffix, params=params)
            if scode != 200:
                raise QueryError(data['message'])
            return data

        if return_generator:
            return unpaginate(get_function,'search',params)
        else:
            return list(unpaginate(get_function,'search',params))

    # ---------------------------------- Helper Functions -------------------------------------- #
    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        temp = self.token
        self.set_token(value)

        try:
            self._sync()
        except QueryError:
            print('Authentication failed. Please check the key')
            print('Reverting to old key')
            self.set_token(temp)

    def _sync(self):
        self.devices = self._devices()
        self.device_ids = [device['spotterId'] for device in self.devices]

    def _devices(self):
        # Helper function to access the devices endpoint
        scode, data = self._get('/devices')

        if scode != 200:
            raise QueryError(data['message'])

        _spotters = data['data']['devices']

        return _spotters

    def _device_radius(self):
        # helper function to access the device radius endpoint
        status_code, data = self._get('device-radius')

        if status_code != 200:
            raise QueryError(data['message'])

        spot_data = data['data']['devices']

        return spot_data

    def _get_all_data(self, worker_names: list, start_date: str = None, end_date: str = None, params: dict = None):
        # helper function to return another function used for grabbing all data from Spotters in a period
        def helper(_name):
            _ids = self.device_ids

            # default to bound values if not included
            st = start_date or '2000-01-01T00:00:00.000Z'
            end = end_date or datetime.utcnow()

            _wrker = worker_wrapper((_name, _ids, st, end, params))
            return _wrker

        # processing the data_types in parallel
        pool = ThreadPool(processes=len(worker_names))
        all_data = pool.map(helper, worker_names)
        pool.close()

        all_data = {name: l for name, l in zip(worker_names, all_data)}

        # if len(all_data) > 0:
        #     all_data.sort(key=lambda x: x['timestamp'])

        return all_data


class WaveDataQuery(SofarConnection):
    """
    General Query class
    """
    _MISSING = object()

    def __init__(self, spotter_id: str, limit: int = 20, start_date=_MISSING, end_date=_MISSING, params=None):
        """
        Query the Sofar API for Spotter data

        :param spotter_id: String id of the Spotter to query for
        :param limit: The limit of data to query. Defaults to 20, max of 100 for frequency data, max of 500 otherwise
        :param start_date: ISO8601 formatted string for start date, otherwise if not included, defaults to
                            a date arbitrarily far back to include all Spotter data
        :param end_date: ISO8601 formatted string for end date, otherwise if not included defaults to present
        :param params: Defaults to None. Parameters to overwrite/add to the default query parameter set
        """
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
            'includeDirectionalMoments': 'false',
            'includeSurfaceTempData': 'false',
            'includeSpikes': 'false',            
            'includeNonObs': 'false',
            'includeMicrophoneData': 'false',
            'includeBarometerData': 'false'
        }
        if params is not None:
            self._params.update(params)

        if self.start_date is not None:
            self._params.update({'startDate': self.start_date})

        if self.end_date is not None:
            self._params.update({'endDate': self.end_date})

    def execute(self):
        """
        Calls the api wave-data endpoint and if successful returns the queried data with the set query parameters

        :return: Data as a dictionary
        """
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

    def barometer(self, include: bool):
        """

        :param include: True if you want the query to include barometer data
        """
        self._params.update({'includeBarometerData': str(include).lower()})

    def microphone(self, include: bool):
        """

        :param include: True if you want the query to include microphone data
        """
        self._params.update({'includeMicrophoneData': str(include).lower()})

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
                     Directional moment data only applies if the Spotter is in full waves/waves spectrum mode. \n
                     Since the query does not include frequency data (of which directional moments are a subset)
                     the data you have requested will not be included. \n
                     Please set includeFrequencyData to true with .frequency(True) if desired. \n""")
        self._params.update({'includeDirectionalMoments': str(include).lower()})


    def surface_temp(self, include: bool):
        """

        :param include: True if you want the query to include surface temp data
        """
        self._params.update({'includeSurfaceTempData': str(include).lower()})

    def spikes(self, include: bool):
        """

        :param include: True if you want the query to include data points exceeding our spike filter
        """
        self._params.update({'includeSpikes': str(include).lower()})

    def smooth_wave_data(self, include: bool):
        """

        :param include: True if you want the query to smooth wave data
        """
        self._params.update({'smoothWaveData': str(include).lower()})

    def smooth_sg_window(self, value: int):
        """

        :param value: Window size of the SG smoothing filter. Must be odd positive int.
        """
        self._params.update({'smoothSGWindow': value})

    def smooth_sg_order(self, value: int):
        """

        :param value: Polynomial order of SG smoothing filter. Positive int > 0.
        """
        self._params.update({'smoothSGOrder': value})

    def interpolate_utc(self, include: bool):
        """

        :param include: True if you want the query to interpolate data to UTC hours time base.
        """
        self._params.update({'interpolateUTC': str(include).lower()})

    def interpolate_period_seconds(self, value: int):
        """

        :param value: Period in seconds of samples after smoothing and/or interpolation.
        """
        self._params.update({'interpolatePeriodSeconds': value})

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
        s = f"Query for {self.spotter_id} \n" + \
            f"  Start: {self.start_date or 'From Beginning'} \n" + \
            f"  End: {self.end_date or 'Til Present'} \n" + \
            "  Params:\n" + \
            f"    id: {self._params['spotterId']}\n" + \
            f"    limit: {self._params['limit']} \n" + \
            f"    waves: {self._params['includeWaves']} \n" + \
            f"    wind: {self._params['includeWindData']} \n" + \
            f"    barometer: {self._params['includeBarometerData']} \n" + \
            f"    sst: {self._params['includeSurfaceTempData']} \n" + \
            f"    microphone: {self._params['includeMicrophoneData']} \n" + \
            f"    track: {self._params['includeTrack']} \n" + \
            f"    frequency: {self._params['includeFrequencyData']} \n" + \
            f"    directional_moments: {self._params['includeDirectionalMoments']} \n"

        return s


# ---------------------------------- Util Functions -------------------------------------- #
def get_and_update_spotters(_api=None):
    """
    :return: A list of the Spotter objects associated with this account
    """
    from itertools import repeat

    api = _api or SofarApi()

    # grab device id's and query for device data
    # initialize Spotter objects
    spot_data = api.devices

    pool = ThreadPool(processes=16)
    spotters = pool.starmap(_spot_worker, zip(spot_data, repeat(api)))
    pool.close()

    return spotters


# ---------------------------------- Workers -------------------------------------- #
def _spot_worker(device: dict, api: SofarApi):
    """
    Worker to grab Spotter data

    :param device: Dictionary containing the Spotter id and name

    :return: Spotter object updated from the Sofar api with its latest data values
    """
    from pysofar.spotter import Spotter

    _id = device['spotterId']
    _name = device['name']
    _api = api

    sptr = Spotter(_id, _name, _api)
    sptr.update()

    return sptr


def worker_wrapper(args):
    """
    Wrapper for creating workers to grab lots of data

    :param args: Tuple of the worker_type: str (ex. 'wind', 'waves', 'frequency', 'track')
                              _ids: list of str, which are the Spotter ids
                              st_date: str, iso 8601 formatted start date of period to query
                              end_date: str, iso 8601 formatted end date of period to query
                              params: dict, query parameters to set

    :return: All data for that type for all Spotters in the queried period
    """
    worker_type, _ids, st_date, end_date, params = args
    queries = [WaveDataQuery(_id, limit=500, start_date=st_date, end_date=end_date, params=params) for _id in _ids]

    # grabbing data from all of the Spotters in parallel
    pool = ThreadPool(processes=16)
    _wrkr = _worker(worker_type)
    worker_data = pool.map(_wrkr, queries)
    pool.close()

    # unwrap list of lists
    worker_data = list(chain(*worker_data))

    if len(worker_data) > 0:
        worker_data.sort(key=lambda x: x['timestamp'])

    return worker_data


def _worker(data_type):
    """
    Worker to grab data from certain data type for a specific query

    :param data_type: The desired data type

    :return: A helper function able to process a query for that specific data type
    """
    def _helper(data_query):
        st = data_query.start_date
        end = data_query.end_date

        # setup the query
        data_query.waves(False)
        getattr(data_query, data_type)(True)

        if data_type == 'frequency':
            dkey = 'frequencyData'
            data_query.directional_moments(True)
        elif data_type == 'surface_temp':
            dkey = 'surfaceTemp'
            data_query.surface_temp(True)
        elif data_type == 'barometer':
            dkey = 'barometerData'
            data_query.barometer(True)
        elif data_type == 'microphone':
            dkey = 'microphoneData'
            data_query.microphone(True)
        else:
            dkey = data_type

        query_data = []

        while st < end:
            _query = data_query.execute()

            results = _query[dkey]

            for dt in results:
                dt.update({'spotterId': _query['spotterId']})

            query_data.extend(results)

            # break if no results are returned
            if len(results) == 0:
                break

            st = results[-1]['timestamp']
            data_query.set_start_date(st)

            # break if start and end dates are the same to avoid potential infinite loop for samples
            # at end time
            if st == end:
                break

        # here query data is a list of dictionaries
        return query_data

    return _helper


def unpaginate( get_function, endpoint_suffix , params )->Dict:
    """
    Generator function to unpaginate a paginated request.

    Note:
    It is a little ugly now with the removing of the endpoint prefix so that
    the _get function can append it again. Right now it looks like the paginated
    server returns http instead of https in the url so this may actually be a
    good thing.

    :param get_function: the _get fuction that takes an endpoint suffic and params as arguments
    :param endpoint_suffix: endpoint to hit from the Sofar Api
    :param params: dict of additional query parameters to write beyond default values

    :return: track data as a list
    """
    suffix = endpoint_suffix
    while True:
        page = get_function( suffix, params)

        for item in page['data']:
            yield item

        if page['metadata']['page']['hasMoreData']:
            url = page['metadata']['page']['nextPage']
            # here we remove the prefix, but keep everything else in the url
            # returned by wavefleet.
            suffix = endpoint_suffix + url.split(endpoint_suffix)[1]

            # parameters are no longer needed as these are already encoded
            # in the given url.
            params = None
        else:
            break
