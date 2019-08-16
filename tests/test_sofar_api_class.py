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


def test_get_and_update_spotters():
    from pysofar.spotter import Spotter
    from pysofar.sofar import get_and_update_spotters

    sptrs = get_and_update_spotters(_api=api)

    assert sptrs is not None
    assert all(map(lambda x: isinstance(x, Spotter), sptrs))


def test_get_all_wave_data():
    st = '2019-05-02'
    end = '2019-07-10'
    dat = api.get_wave_data(start_date=st, end_date=end)

    assert dat is not None

    assert isinstance(dat, list)


def test_get_all_wind_data():
    # st = '2019-05-02'
    # end = '2019-07-10'
    # dat = api.get_wind_data(start_date=st, end_date=end)
    dat = api.get_wind_data()

    assert dat is not None
    # TODO: More testing here of results?
    #print(dat)
    assert isinstance(dat, list)


