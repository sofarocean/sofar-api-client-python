"""
This file is part of pysofar: A client for interfacing with Sofar Oceans Spotter API

Contents: Tests for device endpoints

Copyright (C) 2019
Sofar Ocean Technologies

Authors: Mike Sosa
"""
from pysofar.sofar import SofarApi

api = SofarApi()
dat = api.get_device_location_data()
devices = api.get_devices()
device_ids = api.get_device_ids()


def test_get_device():
    # test that the sofar api can correctly grab its related devices
    assert devices is not None
    assert isinstance(devices, list)
    assert all(map(lambda x: isinstance(x, dict), devices))


def test_get_device_ids():
    # test that the device ids are returned correctly
    assert api.get_device_ids() is not None
    assert isinstance(api.get_device_ids(), list)


def test_get_device_location_data():
    # test that the api can retrieve device location data
    assert dat is not None
    assert len(dat) != 0
    assert all(map(lambda x: isinstance(x, dict), dat))


def test_valid_location_data():
    # test that the location data returned is formatted correctly
    spotter = dat.pop()
    assert 'spotterId' in spotter
    assert 'location' in spotter

    loc = spotter['location']

    assert 'lat' in loc
    assert 'lon' in loc
    assert 'timestamp' in loc
