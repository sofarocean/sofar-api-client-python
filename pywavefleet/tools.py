def time_stamp_to_epoch( date_string ):
    """

    :param date_string: Date string formatted as iso
    :return:
    """
    import time
    import calendar

    return calendar.timegm(time.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ'))