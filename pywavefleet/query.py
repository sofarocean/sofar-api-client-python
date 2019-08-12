from pywavefleet.api import SofarConnection
from pywavefleet.wavefleet_exceptions import QueryError
from pywavefleet.tools import parse_date


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
