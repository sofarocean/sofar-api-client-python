"""
This file is part of pysofar: A client for interfacing with Sofar Oceans Spotter API

Contents: Tests for device endpoints

Copyright (C) 2019
Sofar Ocean Technologies

Authors: Mike Sosa
"""
from pysofar.sofar import WaveDataQuery

st = '2019-05-02'
end = '2019-05-10'
q = WaveDataQuery('SPOT-0196', limit=100, start_date=st, end_date=end)
q.wind(True)


def test_query_execute():
    # basic query
    # returned earliest data first
    response = q.execute()
    assert response is not None
    assert isinstance(response, dict)

    assert 'waves' in response
    assert 'wind' in response


def test_query_no_dates():
    # resturned latest data first
    q.limit(10)
    q.clear_start_date()
    q.clear_end_date()

    response = q.execute()
    assert response is not None
    assert isinstance(response, dict)

    assert 'waves' in response
    assert 'wind' in response


def test_query_no_start():
    # resturned
    q.limit(10)

    q.clear_start_date()
    q.set_end_date(end)

    response = q.execute()
    assert response is not None
    assert isinstance(response, dict)

    assert 'waves' in response
    assert 'wind' in response


def test_query_no_end():
    # returned
    q.limit(10)

    q.clear_end_date()
    q.set_start_date(st)

    response = q.execute()
    assert response is not None
    assert isinstance(response, dict)

    assert 'waves' in response
    assert 'wind' in response