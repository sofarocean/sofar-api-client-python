"""
Classes for representing devices and data grabbed from the api
"""
from pywavefleet.sofar import SofarApi
from pywavefleet.query import Query


# --------------------- Devices ----------------------------------------------#
class Spotter:
    def __init__(self, spotter_id: str, name: str):
        self.id = spotter_id
        self.name = name

        self.mode = None
        self.data = None
        self.lat = None
        self.lon = None
        self.update_timestamp = None

        self.battery_power = None
        self.solar_voltage = None
        self.humidity = None

        self._session = SofarApi()

    # -------------------------- Properties -------------------------------------- #
    @property
    def mode(self):
        """
        The tracking type of the spotter.
        3 Modes are possible:
            - waves_standard
            - waves_spectrum (Includes spectrum data)
            - tracking

        :return: The current mode of the spotter
        """
        return self.mode

    @mode.setter
    def mode(self, value):
        if value == 'full':
            self.mode = 'waves_spectrum'
        elif value == 'waves':
            self.mode = 'waves_standard'
        elif value == 'track':
            self.mode = 'tracking'
        else:
            raise Exception('Invalid Mode')

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
        Updates the spotter's data values.

        :return: The updated spotter object
        """
        # TODO: also add the latest data for this (Since it does return it)
        data = self._session.get_latest_data(self.id)

        self.name = data['spotterName']
        self.mode = self.mode(data['payloadType'])
        self.lat = data['track']['latitude']
        self.lon = data['track']['longitude']
        self.update_timestamp = data['track']['timestamp']

        self.battery_power = data['batteryPower']
        self.solar_voltage = data['solarVoltage']
        self.humidity = data['humidity']

    def grab_data(self, limit: int = 20,
                  start_date: str = None, end_date: str = None,
                  include_waves: bool = True, include_wind: bool = False,
                  include_track: bool = False, include_frequency_data: bool = False,
                  include_directional_moments: bool = False):
        _query = Query(self.id, limit, start_date, end_date)
        _query.waves(include_waves)
        _query.wind(include_wind)
        _query.track(include_track)
        _query.frequency(include_frequency_data)
        _query.directional_moments(include_directional_moments)

        data = _query.execute()
        self.data = data
        # TODO: Set data here
        return data



# TODO: Get devices (really called devices)
# TODO: Latest data
# TODO: Handle iso string vs python datatime
# 