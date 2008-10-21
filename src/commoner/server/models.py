from django.db import models

from django.contrib.auth.models import User

SREG_METADATA = (
    ('nickname', 'screenname'),
    ('email',    'email'),
    ('fullname', 'fullname'),
    ('dob',      'dob'),
    ('gender',   'gender'),
    ('postcode', 'postcode'),
    ('country',  'country'),
    ('language', 'language'),
    ('timezone', 'timezone'),
    )

class TrustedRelyingParty(models.Model):

    user = models.ForeignKey(User, related_name='trusted_parties')
    root = models.CharField(max_length=255)

    def __unicode__(self):
        return self.root

class TrustedMetadata(models.Model):

    relying_party = models.ForeignKey(TrustedRelyingParty, 
                                      related_name='metadata')
    field_name = models.CharField(max_length=100, choices=SREG_METADATA)

    def __str__(self):
        return self.field_name
