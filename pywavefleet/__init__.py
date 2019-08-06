import os
import dotenv

# config values
_endpoint = None
_wavefleet_token = None

userpath = os.path.expanduser("~")
enviromentFile = os.path.join(userpath,'sofar_api.env')
dotenv.load_dotenv(enviromentFile)
token = os.getenv('WF_API_TOKEN')

_wavefleet_token = token
_endpoint = 'https://wavefleet.spoondriftspotter.co/api'


def get_token():
    return _wavefleet_token


def get_endpoint():
    return _endpoint


def time_stamp_to_epoch(date_string):
    #
    # 2019-03-11T22:09:01.000Z
    #
    import time
    import calendar

    return calendar.timegm(time.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ'))
