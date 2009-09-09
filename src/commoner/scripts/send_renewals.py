"""
This module is used to send renewal letters to profiles that are
approaching expiration.  When ran, this script will send email
reminders to all Commoner Profiles that will be expiring exactly 
in 1 month and those that will be expiring in 15 days.  For the
script to effectively reminder all of our account holders, it
will need to be schedule to run ONCE per day, every day.
"""

import sqlalchemy
from datetime import datetime, timedelta

os.environ['DJANGO_SETTINGS_MODULE'] = 'commoner.settings'

from commoner.profiles.models import CommonerProfile

today = datetime.now()
month_from_today = today + timedelta(days=30)
fifteen_days = today + timedelta(days=15)

# look for profiles expiring in the next 30 days from now
first_reminders = CommonerProfile.objects.filter(
                      expires__day = month_from_today.day,
                      expires__month = month_from_today.month,
                      expires__year = month_from_today.year)

last_reminders = CommonerProfile.objects.filter(
                      expires__day = fifteen_days.day,
                      expires__month = fifteen_days.month,
                      expires__year = fifteen_days.year)

print "First Reminders sent to:"
for p in first_reminders:
    print "%s - %s" % (p.user.username, p.expires,)

print "Last Reminders sent to:"
for p in last_reminders:
    print "%s - %s" % (p.user.username, p.expires,)

