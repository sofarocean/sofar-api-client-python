"""
This file is part of pysofar: A client for interfacing with Sofar Oceans Spotter API

Contents: Classes for representing devices and data grabbed from the api

Copyright (C) 2019
Sofar Ocean Technologies

Authors: Mike Sosa
"""
from pysofar.sofar import SofarApi, WaveDataQuery


# --------------------- Devices ----------------------------------------------#
class Spotter:
    """
    Class to represent a spotter object
    """
    def __init__(self, spotter_id: str, name: str):
        """

        :param spotter_id: The spotter id as a string
        :param name: The name of the spotter
        """
        self.id = spotter_id
        self.name = name

        # cached spotter data
        self._data = None

        # spotter parameters
        self._mode = None
        self._latitude = None
        self._longitude = None
        self._battery_power = None
        self._battery_voltage = None
        self._solar_voltage = None
        self._humidity = None
        self._timestamp = None

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
        return self._mode

    @mode.setter
    def mode(self, value):
        """
        Sets the mode of the spotter

        :param value: Either 'full , 'waves', or 'track' else throws exception
        """
        if value == 'full':
            self._mode = 'waves_spectrum'
        elif value == 'waves':
            self._mode = 'waves_standard'
        elif value == 'track':
            self._mode = 'tracking'
        else:
            raise Exception('Invalid Mode')

    @property
    def lat(self):
        """

        :return: The most recent latitude value (since updating)
        """
        return self._latitude

    @lat.setter
    def lat(self, value): self._latitude = value

    @property
    def lon(self):
        """

        :return: The most recent longitude value (since updating)
        """
        return self._longitude

    @lon.setter
    def lon(self, value): self._longitude = value

    @property
    def battery_voltage(self):
        """

        :return: Battery voltage of the spotter
        """
        return self._battery_voltage

    @battery_voltage.setter
    def battery_voltage(self, value): self._battery_voltage = value

    @property
    def battery_power(self):
        """

        :return: The most recent battery_power value (since updating)
        """
        return self._battery_power

    @battery_power.setter
    def battery_power(self, value): self._battery_power = value

    @property
    def solar_voltage(self):
        """

        :return: The most recent solar voltage level (since updating)
        """
        return self._solar_voltage

    @solar_voltage.setter
    def solar_voltage(self, value): self._solar_voltage = value

    @property
    def humidity(self):
        """

        :return: The most recent humidity value (since updating)
        """
        return self._humidity

    @humidity.setter
    def humidity(self, value): self._humidity = value

    @property
    def timestamp(self):
        """
        The time value at which the current spotter last recorded data

        :return: ISO8601 formatted string
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value): self._timestamp = value

    @property
    def data(self):
        """

        :return: Cached data from the latest update
        """
        return self._data

    @data.setter
    def data(self, value): self._data = value

    # -------------------------- API METHODS -------------------------------------- #
    def change_name(self, new_name: str):
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
        from pysofar.tools import parse_date
        self._session.grab_datafile(self.id, parse_date(start_date), parse_date(end_date))

    def update(self):
        """
        Updates this spotter's attribute values.

        :return: The data last recorded by the current spotter
        """
        # TODO: also add the latest data for this (Since it does return it)
        _data = self._session.get_latest_data(self.id)

        self.name = _data['spotterName']
        self._mode = _data['payloadType']
        self._latitude = _data['track'][-1]['latitude']
        self._longitude = _data['track'][-1]['longitude']
        self._timestamp = _data['track'][-1]['timestamp']

        self._battery_power = _data['batteryPower']
        self._battery_voltage = _data['batteryVoltage']
        self._solar_voltage = _data['solarVoltage']
        self._humidity = _data['humidity']

        wave_data = _data['waves']
        track_data = _data['track']
        freq_data = _data['frequencyData']

        results = {
            'wave': wave_data[-1] if len(wave_data) > 0 else None,
            'tracking': track_data[-1] if len(track_data) > 0 else None,
            'frequency': freq_data[-1] if len(freq_data) > 0 else None
        }
        self._data = results

    def latest_data(self, include_wind: bool = False, include_directional_moments: bool = False):
        """

        :param include_wind:
        :param include_directional_moments:
        :return:
        """
        _data = self._session.get_latest_data(self.id,
                                              include_wind_data=include_wind,
                                              include_directional_moments=include_directional_moments)

        wave_data = _data['waves']
        track_data = _data['track']
        freq_data = _data['frequencyData']

        results = {
            'wave': wave_data[-1] if len(wave_data) > 0 else None,
            'tracking': track_data[-1] if len(track_data) > 0 else None,
            'frequency': freq_data[-1] if len(freq_data) > 0 else None
        }

        return results

    def grab_data(self, limit: int = 20,
                  start_date: str = None, end_date: str = None,
                  include_waves: bool = True, include_wind: bool = False,
                  include_track: bool = False, include_frequency_data: bool = False,
                  include_directional_moments: bool = False):
        """
        Grabs the requested data for this spotter based on the given keyword arguments

        :param limit: The limit for data to grab. Defaults to 20, For frequency data max of 100 samples at a time,
                      else, 500 samples. If you send values over the limit, it will automatically limit for you
        :param start_date: ISO 8601 formatted date string. If not included defaults to beginning of spotters history
        :param end_date: ISO 8601 formatted date string. If not included defaults to end of spotter history
        :param include_waves: Defaults to True. Set to False if you do not want the wave data in the returned response
        :param include_wind: Defaults to False. Set to True if you want wind data in the returned response
        :param include_track: Defaults to False. Set to True if you want tracking data in the returned response
        :param include_frequency_data: Defaults to False. Only applies if the spotter is in 'Full Waves mode' Set to
                                        True if you want frequency data in the returned response
        :param include_directional_moments: Defaults to False. Only applies if the spotter is in 'Full Waves mode' and
                                            'include_frequency_data' is True. Set True if you want the frequency data
                                            returned to also include directional moments

        :return: Data as a json based on the given query paramters
        """
        _query = WaveDataQuery(self.id, limit, start_date, end_date)
        _query.waves(include_waves)
        _query.wind(include_wind)
        _query.track(include_track)
        _query.frequency(include_frequency_data)
        _query.directional_moments(include_directional_moments)

        _data = _query.execute()

        return _data
