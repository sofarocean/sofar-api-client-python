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
from pysofar.spotter import Spotter

class UserRestDevicesTest(unittest.TestCase):
    def testCellularSignalMetricsFromSpotter(self):
        spot = Spotter(self._cellular_id, self._cellular_id)
        data = spot.grab_cellular_signal_metrics()
        self.assertTrue(data)

    def testCellularSignalMetricsParameters(self):
        if not self._cellular_id:
            self.skipTest("could not find a likely cellular Spotter")
        my_limit = 30
        my_start_epoch_ms=1727488168
        my_end_epoch_ms=1727995013
        my_order = True

        query = CellularSignalMetricsQuery(
            self._cellular_id,
            limit=my_limit,
            order_ascending=my_order,            
            start_epoch_ms=my_start_epoch_ms,
            end_epoch_ms=my_end_epoch_ms,
        )
        data = query.execute(return_raw=True)
        self.assertIn('options', data)
        # the API response feeds us back the options we gave it,
        # but in the case of this API, the response keys are different
        # from the request parameter keys.
        # sc-208038
        options = data['options']
        self.assertEqual(options['spotterId'], self._cellular_id)
        self.assertEqual(options['limit'], my_limit)
        self.assertNotIn('order_ascending', options)
        self.assertIn('orderAscending', options)
        self.assertEqual(options['orderAscending'], True)
        self.assertIn('startEpochMs', options)   #  !! unexpected
        self.assertIn('endEpochMs', options)     #  !! unexpected
        self.assertIsNone(options['startEpochMs'])
        self.assertIsNone(options['endEpochMs'])
        self.assertIn('sinceEpochMs', options)
        self.assertIn('beforeEpochMs', options)
        self.assertEqual(options['sinceEpochMs'], my_start_epoch_ms)
        self.assertEqual(options['beforeEpochMs'], my_end_epoch_ms)

    def testCellularSignalMetricsRequest(self):
        if not self._cellular_id:
            self.skipTest("could not find a likely cellular Spotter")

        query = CellularSignalMetricsQuery(self._cellular_id)
        data = query.execute()

    def setUp(self):
        self._api = SofarApi()
        self._devices = self._api.devices
        self._device_ids = self._api.device_ids
        self._cellular_id = self._findPossibleCellularDevice()

    def _findPossibleCellularDevice(self):
        """
        Guess that a Spotter ending in C might be a cellular Spotter
        
        This is /not/ the best way of doing this.
        """
        return next((spot_id for spot_id in self._device_ids if spot_id.endswith('C')), None)
