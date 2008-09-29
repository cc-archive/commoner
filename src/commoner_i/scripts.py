import os
from django.core import management

def manage():

    import commoner_i.settings as mod

    management.execute_manager(mod)
