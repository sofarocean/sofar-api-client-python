# config values
_endpoint = None
_wavefleet_token = None


def set_token(token):
    _wavefleet_token = token


def set_endpoint(url):
    _endpoint = url


def get_token():
    return _wavefleet_token


def get_endpoint():
    return _endpoint
