import os

DEBUG = TEMPLATE_DEBUG = False

ADMINS = (
    ('Creative Commons Webmaster', 'webmaster@creativecommons.org'),
)

MANAGERS = ADMINS

if not DEBUG:
    SEND_BROKEN_LINK_EMAILS = True

from commoner.settings import DATABASE_ENGINE, DATABASE_NAME
from commoner.settings import DATABASE_USER, DATABASE_PASSWORD
from commoner.settings import DATABASE_HOST, DATABASE_PORT

TIME_ZONE = 'America/Chicago'

LANGUAGE_CODE = 'en-us'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), '..','..','static','m',)

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/m/'


# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Don't share this with anybody.
SECRET_KEY = 'go7++&w46=wjfdsv6rm68=4rx$$o@mx9k3-bk82$nt7m$i8@8d'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)


ROOT_URLCONF = 'commoner_i.urls'

INSTALLED_APPS = ('commoner.profiles','commoner.works')

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), "templates"),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "commoner.util.base_url_context",
    )

AUTH_PROFILE_MODULE = "profiles.CommonerProfile"


# Location (relative to MEDIA_ROOT) where all user-uploaded media are stored.
# The same rules apply to this as to MEDIA_URL as well -- there must be a
# trailing slash.
USER_STORAGE = 'user/'
