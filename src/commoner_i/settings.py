import os
from commoner.settings import *

MEDIA_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'static')
    )

ROOT_URLCONF = 'commoner_i.urls'
# DEBUG = False
