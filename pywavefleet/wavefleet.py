from . import get_endpoint, get_token


class WaveFleet:
    def __init__(self):
        self.token = get_token()
        self.endpoint = get_endpoint()

    def get_devices(self):
        import json
        import requests

        headers = {'token': self.token, 'Content-Type': 'appication/json'}
        data = json.loads(requests.get(self.endpoint + '/devices', headers=headers).text)

        spotters = []
        for device in data['data']['devices']:
            # TODO: Check if actually valid?
            spotters.append(device['spotterId'])

        return spotters
