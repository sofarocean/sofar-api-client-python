"""
This file is part of pysofar: 
A client for interfacing with Sofar Ocean Technologies Spotter API

Contents: Tests for device endpoints

Copyright (C) 2019-2023
Sofar Ocean Technologies

Authors: Mike Sosa et al
"""
from pysofar import wavefleet_exceptions
from pysofar.sofar import SofarApi
from unittest.mock import patch


# The custom token will fail to authenticate so use a mock to bypass the `_sync step`
with patch.object(SofarApi, '_sync', return_value=None) as mock_method:
    custom_api = SofarApi(custom_token='custom_api_token_here')

def test_custom_api():
    # test that custom api token is set
    assert custom_api.token == 'custom_api_token_here'


api = SofarApi()
latest_dat = api.get_latest_data('SPOT-30344R', include_wind_data=True)


def test_get_latest_data():
    # test basic that latest_data is able to be queried
    assert latest_dat is not None
    assert isinstance(latest_dat, dict)
    assert 'waves' in latest_dat
    assert 'wind' in latest_dat
    assert 'track' in latest_dat
    assert 'frequencyData' in latest_dat


def test_get_and_update_spotters():
    # Test that spotter objects are able to be created and updated
    from pysofar.spotter import Spotter
    from pysofar.sofar import get_and_update_spotters

    sptrs = get_and_update_spotters(_api=api, _processes=2)

    assert sptrs is not None
    assert all(map(lambda x: isinstance(x, Spotter), sptrs))


def test_get_all_wave_data():
    # Test that all wave data is able to be queried in a time range
    st = '2019-05-02'
    end = '2019-07-10'
    dat = api.get_wave_data(start_date=st, end_date=end)

    assert dat is not None
    assert isinstance(dat, dict)
    assert 'waves' in dat
    assert len(dat['waves']) > 0


def test_get_all_wind_data():
    # Test that all wind data over all time is able to be queried
    st = '2021-05-02'
    end = '2021-07-10'
    dat = api.get_wind_data(start_date=st, end_date=end)

    assert dat is not None
    assert isinstance(dat, dict)
    assert 'wind' in dat
    assert len(dat['wind']) > 0


def test_get_all_tracking_data():
    # Test that all tracking data is able to be queried in a time range
    st = '2021-05-02'
    end = '2021-06-10'
    dat = api.get_track_data(start_date=st, end_date=end)

    assert dat is not None
    assert isinstance(dat, dict)
    assert 'track' in dat
    assert len(dat['track']) > 0


def test_get_all_frequency_data():
    # Test that all frequency data is able to be queried in a time range
    st = '2021-06-08'
    end = '2021-06-10'
    dat = api.get_frequency_data(start_date=st, end_date=end)

    assert dat is not None
    assert isinstance(dat, dict)
    assert 'frequency' in dat
    assert len(dat['frequency']) > 0


def test_get_all_data():
    # Test that grabbing data from all spotters from all data types works
    st = '2019-01-18'
    end = '2019-01-25'

    dat = api.get_all_data(start_date=st, end_date=end)

    assert dat is not None
    assert isinstance(dat, dict)
    assert len(dat.keys()) == 4
    assert 'waves' in dat
    assert 'wind' in dat
    assert 'track' in dat
    assert 'frequency' in dat
    
def test_get_sensor_data():
    # Test that getting sensor data in a time range works
    spotter_id = 'SPOT-30081D'
    st = '2022-08-01'
    end = '2022-08-02'
    
    dat = api.get_sensor_data(spotter_id, start_date=st, end_date=end)
    
    assert dat is not None
    print(dat)
    assert 'sensorPosition' in dat[-1]
    
