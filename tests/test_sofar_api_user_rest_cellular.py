"""
This file is part of pysofar: A client for interfacing with Sofar Ocean's Spotter API

Contents: Tests for user-rest/cellular-signal-metrics endpoint

Copyright (C) 2024
Sofar Ocean Technologies

Authors: Tim Johnson
"""
import json
import unittest

from pysofar.sofar import SofarApi, CellularSignalMetricsQuery

class UserRestDevicesTest(unittest.TestCase):

    def testCellularSignalMetricsRequest(self):
        if not self._cellular_id:
            self.skipTest("could not find a likely cellular Spotter")

        query = CellularSignalMetricsQuery(self._cellular_id)
        data = query.execute()
        print(json.dumps(data[0], indent=2))

    def setUp(self):
        self._api = SofarApi()
        # dat = api.get_device_location_data()
        self._devices = self._api.devices
        self._device_ids = self._api.device_ids
        self._cellular_id = self._findPossibleCellularDevice()

    def _findPossibleCellularDevice(self):
        """
        Guess that a Spotter ending in C might be a cellular Spotter
        
        This is /not/ the best way of doing this.[A
        """
        return next((spot_id for spot_id in self._device_ids if spot_id.endswith('C')), None)
        