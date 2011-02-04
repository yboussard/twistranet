from sorl.thumbnail.images import ImageFile
from django.core.urlresolvers import reverse
from django.conf import settings
from twistranet.twistapp.lib.log import *

@property
def absolute_url(self):
    """
    return thumbnail absolute_url
    """
    base_url = settings.BASE_URL
    return '%s%s' %(base_url, self.storage.url(self.name))

log.info("Patched sorl.thumbnail.image.ImageFile.url to get absolute url")
ImageFile.old_url = ImageFile.url
ImageFile.url = absolute_url