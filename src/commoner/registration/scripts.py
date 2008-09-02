import optparse

from commoner.registration.models import PartialRegistration

def _opt_parser():
    """Create the Option Parser and return it."""

    parser = optparse.OptionParser()
    parser.add_option('-l', '--last-name', dest='lastname')
    parser.add_option('-f', '--first-name', dest='firstname')
    parser.add_option('-e', '--email', dest='email')
    parser.add_option('-s', '--send', dest='send_welcome', 
                      action='store_true')

    parser.set_defaults(
        lastname = None,
        firstname = None,
        email = None,
        send_welcome = True)

    return parser

def cli():
    """Command line interface for creating a partial registration
    and sending the welcome email."""


    (options, args) = _opt_parser().parse_args()

    if None in (options.lastname, options.firstname, options.email):
        # a required value is missing
        raise Exception("lastname, firstname and email must be supplied.")

    PartialRegistration.objects.create_registration(
        options.email, options.lastname, options.firstname, 
        options.send_welcome)
