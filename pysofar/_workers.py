"""
This file is part of pysofar: A client for interfacing with Sofar Oceans Spotter API

Contents: Tests for testing utility functions

Copyright (C) 2019
Sofar Ocean Technologies

Authors: Mike Sosa
"""
from multiprocessing.pool import ThreadPool
from datetime import datetime
from pysofar.tools import parse_date


def _data_worker(data_query):
    def helper(_type):
        q = data_query
        q.waves(False)

        if _type == 'waves':
            q.waves(True)
            return _wave_worker(q)
        elif _type == 'winds':
            q.wind(True)
            return _wind_worker(q)
        elif _type == 'track':
            q.track(True)
            return _track_worker(q)
        else:
            q.frequency(True)
            return _frequency_worker

    pool = ThreadPool(processes=4)
    results = pool.map(helper, ['waves', 'winds', 'track', 'frequency'])
    pool.close()

    waves, winds, track, frequency = results

    return waves, winds, track, frequency


def _data_worker_helper(query_param, data_query, earliest: bool=False):

    if not earliest:
        st = query_param


def _wave_worker(data_query):
    # defaults to given start date or start of 2000
    st = data_query.start_date
    end = data_query.end_date

    results = []

    while st < end:
        _q = data_query.execute()
        lim = _q['limit']

        w_data = _q['waves']
        if len(w_data) == 0 or len(w_data) < lim:
            # no more results
            break

        results.extend(w_data)

        # tighten time increment
        end = parse_date(w_data[0]['timestamp'])

    results.reverse()
    return results


def _wind_worker(data_query):
    # defaults to given start date or start of 2000
    st = data_query.start_date
    end = data_query.end_date


    # data_query.set_start_date(st)

    results = []

    while st < end:
        if end is not None:
            data_query.set_end_date(end)
        _q = data_query.execute()
        lim = _q['limit']

        w_data = _q['wind']
        if len(w_data) == 0 or len(w_data) < lim:
            # no more results
            break

        results.extend(w_data)

        # tighten time increment
        end = parse_date(w_data[0]['timestamp'])

    results.reverse()
    return results


def _track_worker(data_query):
    st = data_query.start_date or '2000-01-01T00:00:00.000Z'
    end = data_query.end_date or parse_date(datetime.utcnow())

    results = []

    while st < end:
        _q = data_query.execute()
        lim = _q['limit']

        w_data = _q['track']
        if len(w_data) == 0 or len(w_data) < lim:
            # no more results
            break

        results.extend(w_data)

        # tighten time increment
        end = parse_date(w_data[0]['timestamp'])

    results.reverse()
    return results


def _frequency_worker(data_query):
    st = data_query.start_date or '2000-01-01T00:00:00.000Z'
    end = data_query.end_date or parse_date(datetime.utcnow())

    results = []

    while st < end:
        _q = data_query.execute()
        lim = _q['limit']

        w_data = _q['frequencyData']
        if len(w_data) == 0 or len(w_data) < lim:
            # no more results
            break

        results.extend(w_data)

        # tighten time increment
        end = parse_date(w_data[0]['timestamp'])

    results.reverse()
    return results
