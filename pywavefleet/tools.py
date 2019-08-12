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

        return datetime.datetime.strptime(date_object, "%Y-%m-%dT%H:%M:%S.%fZ").isoformat(timespec="milliseconds")
    elif isinstance(date_object, datetime.datetime):
        return date_object.isoformat(timespec="milliseconds")
    else:
        raise Exception('Invalid Date Format')
