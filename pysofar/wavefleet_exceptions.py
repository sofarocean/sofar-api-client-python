"""
This file is part of pysofar: A client for interfacing with Sofar Oceans Spotter API

Contents: Exception classes

Copyright (C) 2019
Sofar Ocean Technologies

Authors: Mike Sosa
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