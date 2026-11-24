def numba_njit(func):
    """
    Decorator that tests if numba is installed and if so, uses it.
    """
    try:
        import logging

        import numba

        numba_logger = logging.getLogger("numba")
        numba_logger.setLevel(logging.WARNING)

        return numba.njit(func)
    except ImportError:
        return func
