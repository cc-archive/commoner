"""
This script will be used to periodically consume the feeds registered by the users.
"""

import sys
import feedparser

from models import Feed, Work

def consume_feed(feed):
    
    """ Iterates over a feed's entries and registers those items as works for the user """
    
    parsed_feed = feedparser.parse(feed.url)
    
    for entry in parsed_feed.entries:
        
        title = entry.title.encode(parsed_feed.encoding, "xmlcharrefreplace")
        url = entry.link.encode(parsed_feed.encoding, "xmlcharrefreplace")
        
        Work.objects.get_or_create(title=title, url=url, 
                                    license_url=feed.license_url,
                                    registration=feed.registration)
    
    return feed
        
def update_feeds():
    
    """ Retrieve all feeds registered and add the new works """
    
    for feed in Feed.objects.filter(is_defunct=False):
        
        consume_feed(feed)