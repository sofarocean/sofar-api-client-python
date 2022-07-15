"""
This file is part of pysofar: A client for interfacing with Sofar Ocean's Spotter API

Contents: Exception classes

Copyright 2019-2022
Sofar Ocean Technologies

Authors: Mike Sosa et al.
"""


class QueryError(Exception):
    """
    Exception raised when a query to the wavefleet api fails.
    """
    pass


class CouldNotRetrieveFile(Exception):
    """
    Query raised when a requested datafile could not be retrieved.
    """
    pass