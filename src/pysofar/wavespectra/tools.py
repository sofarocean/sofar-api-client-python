from datetime import datetime, timezone
import typing

def datetime_to_iso_time_string(time: datetime):
    return time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def to_datetime(time: typing.Union[float, int, datetime, str]):
    if time is None:
        return None

    if isinstance(time, datetime):
        return time.astimezone(timezone.utc)
    elif isinstance(time, str):
        if time[-1] == "Z":
            # From isoformat does not parse "Z" as a valid timezone designator
            time = time[:-1] + "+00:00"
        try:
            return datetime.fromisoformat(time)
        except ValueError as e:
            return datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%f%z")
    else:
        return datetime.fromtimestamp(time, tz=timezone.utc)

