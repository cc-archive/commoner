from django.http import HttpResponse, Http404

from django.contrib.syndication.feeds import Feed
from django.contrib.syndication.feeds import FeedDoesNotExist
from django.utils.feedgenerator import Atom1Feed
from django.contrib.sites.models import Site

from django.contrib.auth.models import User

import models

MAX_FEED_LENGTH=20

class WorksFeed(Feed):
    feed_type = Atom1Feed

    def get_object(self, params):
        """Get the user object."""

        if len(params) != 1:
            return None

        return User.objects.get(username__exact=params[0])

    def title(self, user):

        if user is not None:
            return "Registered Works for %s" % user.get_profile().display_name()
        else:
            return "Registered Works"

    def link(self, user):

        if not user:
            return "/"

        return user.get_profile().get_absolute_url()

    def description(self, user):
        return ""

    def items(self, user):

        if user is not None:
            return models.Work.objects.filter(
                registration__owner__exact = user.id)[:MAX_FEED_LENGTH]
        else:
            # all works registrations
            return models.Work.objects.all()[:MAX_FEED_LENGTH]

class RecentUpdatesFeed(Feed):
    
    feed_type = Atom1Feed
    title = "Recently Updated Works"    
    link = ""
    
    def description(self):
        return ""
    
    def items(self):
        return models.Work.objects.order_by("-updated")[:MAX_FEED_LENGTH]

def user_works_feed(request, username=None):
    """Wrap the Django feed framework to bend it to our URL-pattern will."""

    slug='works'

    try:
        feedgen = WorksFeed(slug, request).get_feed(username)
    except FeedDoesNotExist:
        raise Http404, "Invalid feed parameters. Slug %r is valid, but other parameters, or lack thereof, are not." % slug

    response = HttpResponse(mimetype=feedgen.mime_type)
    feedgen.write(response, 'utf-8')
    return response

def recent_updates_feed(request):
    """ Wrap the Django feed framework to bend it to our URL-pattern will. """    
    feedgen = RecentUpdatesFeed(slug='updates', request=request).get_feed()
    response = HttpResponse(mimetype=feedgen.mime_type)
    feedgen.write(response, 'utf-8')
    return response