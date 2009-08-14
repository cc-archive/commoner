import sys
import optparse

import commoner.registration.models
from commoner.registration.models import PartialRegistration

def _opt_parser():
    """Create the Option Parser and return it."""

    parser = optparse.OptionParser()
    parser.add_option('-l', '--last-name', dest='lastname')
    parser.add_option('-f', '--first-name', dest='firstname')
    parser.add_option('-e', '--email', dest='email')
    parser.add_option('-t', '--transaction', dest='transaction')
    parser.add_option('-s', '--send', dest='send_welcome', 
                      action='store_true')

    parser.set_defaults(
        lastname = None,
        firstname = None,
        email = None,
        transaction = None,
        send_welcome = True)

    return parser

def register():
    """Command line interface for creating a partial registration
    and sending the welcome email."""


    (options, args) = _opt_parser().parse_args()

    if None in (options.lastname, options.firstname, options.email):
        # a required value is missing
        raise Exception("lastname, firstname, and email must be supplied.")

    PartialRegistration.objects.create_registration(
        options.transaction, options.email, 
        options.lastname, options.firstname, 
        options.send_welcome)

def welcome():
    """Re-send the welcome email for a partial registration."""

    email = sys.argv[-1]

    try:
        registration = PartialRegistration.objects.get(email=email)
    except commoner.registration.models.PartialRegistration.DoesNotExist:
        print "Could not find registration."
        sys.exit(1)

    if registration.complete:
        print "Registration already complete; cannot re-send welcome."
        sys.exit(1)

    PartialRegistration.objects.send_welcome(registration)