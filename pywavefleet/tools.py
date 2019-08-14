import time
import calendar
import datetime


def time_stamp_to_epoch( date_string ):
    """

    :param date_string: Date string formatted as iso
    :return:
    """
    return calendar.timegm(time.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ'))


def parse_date(date_object):
    """

    :param date_object: Give in utc format, either epoch, string, or datetime object
    :return: String date formatted in ISO 8601 format
    """
    if isinstance(date_object, (int, float)):
        return datetime.datetime.utcfromtimestamp(date_object).isoformat(timespec="milliseconds")
    elif isinstance(date_object, str):
        # time includes microseconds
        if "T" not in date_object:
            return datetime.datetime.strptime(date_object, "%Y-%m-%d").isoformat(timespec="milliseconds")

        if "." not in date_object:
            return datetime.datetime.strptime(date_object, "%Y-%m-%dT%H:%M:%S").isoformat(timespec="milliseconds")

        return datetime.datetime.strptime(date_object, "%Y-%m-%dT%H:%M:%S.%f%z").isoformat(timespec="milliseconds")
    elif isinstance(date_object, datetime.datetime):
        return date_object.isoformat(timespec="milliseconds")
    else:
        raise Exception('Invalid Date Format')


def haversine(point_1: tuple, point_2: tuple):
    """

    :param point_1: Tuple of (lat, lon)
    :param point_2: Tuple of (lat, lon)

    :return: Distance between the two points in meters
    """
    from math import sin, cos, asin, radians, sqrt

    earth_rad = 6371008.8

    lat1, lon1 = map(radians, point_1)
    lat2, lon2 = map(radians, point_2)

    d_phi = lat2 - lat1
    d_lambda = lon2 - lon1

    a = sin(d_phi / 2.0)**2 + cos(lat1)*cos(lat2)*sin(d_lambda/2.0)**2

    return 2 * earth_rad * asin(sqrt(a))

