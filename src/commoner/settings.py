import os

DEBUG = TEMPLATE_DEBUG = True

ADMINS = (
    ('Nathan R. Yergler', 'nathan@creativecommons.org'),
    ('Creative Commons Webmaster', 'webmaster@creativecommons.org'),
)

MANAGERS = ADMINS

if not DEBUG:
    SEND_BROKEN_LINK_EMAILS = True

DATABASE_ENGINE = 'mysql'

DATABASE_NAME = 'commoner'
DATABASE_USER = 'root'             # Not used with sqlite3.
DATABASE_PASSWORD = 'doigoid'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

if DEBUG:
    DATABASE_NAME='commoner_testing'

TIME_ZONE = 'America/Chicago'

LANGUAGE_CODE = 'en-us'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), '..','..','static','m',)

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/m/'

# Legal documents like the Terms of Service
LEGAL_ROOT = os.path.join(os.path.dirname(__file__), '..','..','static','l',)
LEGAL_URL = '/l/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Don't share this with anybody.
SECRET_KEY = 'your-secret-key-here'

MIDDLEWARE_CLASSES = (
    'commoner.middleware.security.SSLMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'commoner.urls'


INSTALLED_APPS = (
    'dmigrations',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'commoner.registration',
    'commoner.profiles',
    'commoner.works',
    'commoner.scraper',
    'commoner.server',
    'commoner.authenticate',
    'commoner.help',
	'commoner.broadcast',
)

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
    "commoner.util.services_url_context",
    "commoner.broadcast.context_processors.messages",
    )

# Migration Settings
DMIGRATIONS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'migrations'))
DISABLED_SYNCDB = True
DMIGRATIONS_MYSQL_ENGINE = 'MyISAM'

# Registration Settings
SITE_ID=1
ACCOUNT_ACTIVATION_DAYS = 14

AUTH_PROFILE_MODULE = "profiles.CommonerProfile"
DEFAULT_FROM_EMAIL = "noreply@creativecommons.net"

LOGIN_REDIRECT_VIEW = 'profile_view'

LOGIN_URL = '/a/login/'
LOGOUT_URL = '/a/login/'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
OPENID_ENABLE_DAYS = 0.25

# Location (relative to MEDIA_ROOT) where all user-uploaded media are stored.
# The same rules apply to this as to MEDIA_URL as well -- there must be a
# trailing slash.
USER_STORAGE = 'user/'

# THUMBNAIL_PATH is a path relative to MEDIA_ROOT where
# thumbnails of user photos are stored
THUMBNAIL_PATH = 't'

# BADGE_BASE_URL defines the root location of Badge views
BADGE_BASE_URL = 'http://i.creativecommons.net/p/'
if DEBUG:
    BADGE_BASE_URL = '/i/p/'

# Uncomment the following line and the corresponding line in urls.py
# to serve badges from the same host.
# BADGE_BASE_URL = '/i/p/'
