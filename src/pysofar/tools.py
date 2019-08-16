"""
This file is part of pysofar: A client for interfacing with Sofar Oceans Spotter API

Contents: Functions useful for date/time related parsing and formatting

Copyright (C) 2019
Sofar Ocean Technologies

Authors: Mike Sosa
"""
import time
import calendar
import datetime


def time_stamp_to_epoch(date_string):
    """

    :param date_string: Date string formatted as iso
    :return:
    """
    return calendar.timegm(time.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%f%z'))


def parse_date(date_object):
    """

    :param date_object: Give in utc format, either epoch, string, or datetime object
    :return: String date formatted in ISO 8601 format
    """
    _date = None

    if isinstance(date_object, (int, float)):
        _date = datetime.datetime.utcfromtimestamp(date_object)
    elif isinstance(date_object, str):
        # time includes microseconds
        formatting = "%Y-%m-%dT%H:%M:%S.%f%z"

        if "Z" not in date_object and "+" not in date_object:
            formatting = "%Y-%m-%dT%H:%M:%S.%f"

        if "." not in date_object:
            formatting = "%Y-%m-%dT%H:%M:%S"

        if "T" not in date_object:
            formatting = "%Y-%m-%d"

        _date = datetime.datetime.strptime(date_object, formatting)
    elif isinstance(date_object, datetime.datetime):
        _date = date_object
    else:
        raise Exception('Invalid Date Format')

    # make zone unaware
    f_string = _date.replace(tzinfo=None).isoformat(timespec="milliseconds")
    return f"{f_string}Z"
