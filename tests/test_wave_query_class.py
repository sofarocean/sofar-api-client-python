"""
This file is part of pysofar: A client for interfacing with Sofar Oceans Spotter API

Contents: Tests for device endpoints

Copyright (C) 2019
Sofar Ocean Technologies

Authors: Mike Sosa
"""
from pysofar.sofar import Query

q = Query('SPOT-0130', limit=100, start_date='2019-05-02', end_date='2019-05-10')
q.wind(True)


def test_query_execute():
    response = q.execute()
    assert response is not None
    assert isinstance(response, dict)

    assert 'waves' in response
    assert 'wind' in response