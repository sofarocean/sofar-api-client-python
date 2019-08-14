"""
This file is part of pysofar: A client for interfacing with Sofar Oceans Spotter API

Contents: Tests for device endpoints

Copyright (C) 2019
Sofar Ocean Technologies

Authors: Mike Sosa
"""
from pysofar.sofar import SofarApi

api = SofarApi()
latest_dat = api.get_latest_data('SPOT-0130', include_wind_data=True)


def test_get_latest_data():
    # test basic that latest_data is able to be queried
    assert latest_dat is not None
    assert isinstance(latest_dat, dict)
    assert 'waves' in latest_dat
    assert 'wind' in latest_dat
    assert 'track' in latest_dat
    assert 'frequencyData' in latest_dat





