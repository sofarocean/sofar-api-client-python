"""
This file is part of pysofar: A client for interfacing with Sofar Oceans Spotter API

Contents: Tests for device endpoints

Copyright (C) 2019
Sofar Ocean Technologies

Authors: Mike Sosa
"""
from pysofar.sofar import SofarApi
from pysofar.spotter import Spotter

api = SofarApi()

device = Spotter('SPOT-0350', '')


def test_spotter_update():
    # tests the spotter updates correctly
    device.update()

    assert device.mode is not None
    assert device.battery_voltage is not None
    assert device.battery_power is not None
    assert device.solar_voltage is not None
    assert device.lat is not None
    assert device.lon is not None
    assert device.humidity is not None


def test_spotter_latest_data():
    # test spotter is properly able to grab the latest data
    dat = device.latest_data()

    assert isinstance(dat, dict)
    assert 'wave' in dat
    assert 'tracking' in dat
    assert 'frequency' in dat

    if device.mode == 'tracking':
        assert dat['tracking'] is not None
    else:
        assert dat['wave'] is not None

        if device.mode == 'waves_full':
            assert dat['frequency'] is not None


def test_spotter_edit():
    # test properties are set and read correctly
    device.mode = 'waves'
    device.battery_power = -1
    device.battery_voltage = 0
    device.solar_voltage = 1
    device.lat = 2
    device.lon = 3
    device.humidity = 5

    assert device.mode == 'waves_standard'
    assert device.battery_power == -1
    assert device.battery_voltage == 0
    assert device.solar_voltage == 1
    assert device.lat == 2
    assert device.lon == 3
    assert device.humidity == 5


def test_spotter_mode():
    # test the spotter mode property is set correctly
    device.mode = 'track'
    assert device.mode == 'tracking'

    device.mode = 'full'
    assert device.mode == 'waves_spectrum'


def test_spotter_grab_data():
    # test spotter can correctly grab data
    dat = device.grab_data(limit=20)
    print(dat)

    assert 'waves' in dat
    assert len(dat['waves']) <= 20
