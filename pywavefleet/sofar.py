"""
Sofar Devices
"""
import json

class Spotter:
    def __init__(self, spotter_id: str, name: str, data: json):
        self.id = id
        self.name = name
        self.data = data
        self.lat = None
        self.lon = None

    @property
    def lat(self):
        return self.lat

    @lat.setter
    def lat(self, latitude):
        self.lat = latitude

    @property
    def lon(self):
        return self.lon

    @lon.setter
    def lon(self, longitude):
        self.lon = longitude

