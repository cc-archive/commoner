import os
from django.core import management

def manage():

    import commoner.settings as mod

    management.execute_manager(mod)


def noop():
    """A no-op callable we can list as a "script" in setup.py in order
    to get the PYTHONPATH configured to our liking."""

