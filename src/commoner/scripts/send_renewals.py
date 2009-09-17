"""
This module is used to send renewal letters to profiles that are
approaching expiration.  When ran, this script will send email
reminders to all Commoner Profiles that will be expiring exactly 
in 1 month and those that will be expiring in 15 days.  For the
script to effectively reminder all of our account holders, it
will need to be schedule to run ONCE per day, every day.
"""
import os
from datetime import datetime, timedelta

os.environ['DJANGO_SETTINGS_MODULE'] = 'commoner.settings'

from commoner.profiles.models import CommonerProfile

today = datetime.now()
month_from_today = today + timedelta(days=30)
fifteen_days = today + timedelta(days=15)

# look for profiles expiring in the next 30 days from now
first_reminders = CommonerProfile.objects.filter(
                      gratis=False,
                      expires__day = month_from_today.day,
                      expires__month = month_from_today.month,
                      expires__year = month_from_today.year)

last_reminders = CommonerProfile.objects.filter(
                      gratis=False,
                      expires__day = fifteen_days.day,
                      expires__month = fifteen_days.month,
                      expires__year = fifteen_days.year)

# send the emails with an elegant one liner :)
map(lambda p: p.send_reminder_email(), first_reminders|last_reminders)

# whatever, this is good enough IMO
print '\n'.join(["%s - %s - %s" % (p.email, p.user, p.expires) for p in first_reminders|last_reminders])
