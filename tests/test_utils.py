"""
This file is part of pysofar: A client for interfacing with Sofar Oceans Spotter API

Contents: Tests for testing utility functions

Copyright (C) 2019
Sofar Ocean Technologies

Authors: Mike Sosa
"""
from datetime import datetime
from pysofar.tools import parse_date, time_stamp_to_epoch


def test_time_stamp_to_epoch():
    ts = '1985-11-15T23:56:12.000Z'
    epoch = time_stamp_to_epoch(ts)

    assert isinstance(epoch, int)
    dt = parse_date(epoch)

    assert dt == ts


def test_parse_date_string():
    # test iso representation parses correctly
    ts = '1985-11-15T12:34:56.000Z'
    dt = parse_date(ts)

    assert dt is not None
    assert dt == '1985-11-15T12:34:56.000+00:00'


def test_parse_date_string_only_days():
    # test Y-M-D parses
    ts = '1985-11-15'
    dt = parse_date(ts)

    assert dt is not None
    assert dt == '1985-11-15T00:00:00.000Z'


def test_parse_date_string_no_milliseconds():
    # test Y-M-DTH:M:S parses
    ts = '1985-11-15T12:34:56'
    dt = parse_date(ts)

    assert dt is not None
    assert dt == '1985-11-15T12:34:56.000Z'


def test_parse_date_datetime():
    # test passing in a datetime works
    ts = datetime(1997, 2, 16, 5, 25)
    dt = parse_date(ts)

    assert dt is not None
    assert dt == '1997-02-16T05:25:00.000Z'
