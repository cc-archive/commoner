import os
from PIL import Image

from django.conf import settings
from django.template import Library

from commoner import util

register = Library()

def _thumbnail(file, x, y):

    miniature = os.path.join(settings.THUMBNAIL_PATH, file.name)
    filename = file.path
    miniature_filename = util.get_storage().path(miniature)
    miniature_url = util.get_storage().url(miniature)

    # see if the full size image is newer than the thumbnail
    if os.path.exists(miniature_filename) and \
            os.path.getmtime(filename) > os.path.getmtime(miniature_filename):
        util.get_storage().delete(miniature)

    # if the image wasn't already resized, resize it
    if not util.get_storage().exists(miniature): 

        # make sure the directories exist
	if not(os.path.exists(os.path.dirname(miniature_filename))):
            os.makedirs(os.path.dirname(miniature_filename))

        image = Image.open(filename)
        image.thumbnail([x, y], Image.ANTIALIAS)
        try:
            image.save(miniature_filename, image.format, quality=90, optimize=1)
        except:
            image.save(miniature_filename, image.format, quality=90)

    return miniature_url

@register.filter
def thumbnail(file, size='104x104'):

    # defining the size
    x, y = [int(x) for x in size.split('x')]

    return _thumbnail(file, x, y)

@register.filter
def scale(file, max_side=150):

    try:
        max_side = float(max_side)

        # calculate the size
        x, y = file.width, file.height

        if x > y:
            # horizontal orientation
            y = int((max_side/x) * y)
            x = int(max_side)
        else:
            # vertical orientation
            x = int((max_side/y) * x)
            y = int(max_side)

        return _thumbnail(file, x, y)
    except Exception, e:
        return file.url


