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