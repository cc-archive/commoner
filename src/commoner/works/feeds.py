from django.http import HttpResponse, Http404

from django.contrib.syndication.feeds import Feed
from django.contrib.syndication.feeds import FeedDoesNotExist
from django.utils.feedgenerator import Atom1Feed




from django.contrib.auth.models import User

import models

class WorksFeed(Feed):
    feed_type = Atom1Feed

    def get_object(self, params):
        """Get the user object."""

        if len(params) != 1:
            raise FeedDoesNotExist

        return User.objects.get(username__exact=params[0])

    def title(self, user):
        return "Registered Works for %s" % user.get_profile().display_name()

    def link(self, user):
        if not user:
            raise FeedDoesNotExist

        return user.get_profile().get_absolute_url()

    def description(self, user):
        return ""

    def items(self, user):

        return models.Work.objects.filter(
            registration__owner__exact = user.id)[:5]


def user_works_feed(request, username):
    """Wrap the Django feed framework to bend it to our URL-pattern will."""

    slug='works'

    try:
        feedgen = WorksFeed(slug, request).get_feed(username)
    except FeedDoesNotExist:
        raise Http404, "Invalid feed parameters. Slug %r is valid, but other parameters, or lack thereof, are not." % slug

    response = HttpResponse(mimetype=feedgen.mime_type)
    feedgen.write(response, 'utf-8')
    return response
